'''
Created on Jul 4, 2015

@author: oleg
'''
import os
import time
from django import forms
from django.contrib.gis import forms as geo_forms
from django.utils.translation import ugettext_lazy as _

import autocomplete_light
from leaflet.forms.widgets import LeafletWidget
from floppyforms import widgets as floppyforms_widgets

from let_me_auth import models
from django.forms.models import BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.image import  Image as pil_image
from django.core.files.uploadedfile import InMemoryUploadedFile
from six import BytesIO

UPLOAD_IMG_ID="new-img-file"




class JcropWidget(floppyforms_widgets.FileInput):
    template_name = 'floppyforms/jcrop_image.html'
    omit_value = False

    class Media:
        # form media, i.e. CSS and JavaScript needed for Jcrop.
        # You'll have to adopt these to your project's paths.
        css = {
            'all': ("css/jquery.Jcrop.min.css",)
        }
        js = (
            "js/jquery.Jcrop.min.js",
        )

    def __init__(self, *args, **kwargs):
        self.preview_height = kwargs.pop('preview_height')
        self.preview_width = kwargs.pop('preview_width')
        super(JcropWidget, self).__init__(*args, **kwargs)

    # fixed Jcrop options; to pass options to Jcrop, use the jcrop_options
    # argument passed to the JcropForm constructor. See example above.
    jcrop_options = {
                                        "onSelect": "storeCoords",
                                        "onChange": "storeCoords",
                                    }

    # HTML template for the widget.
    #
    # The widget is constructed from the following parts:
    #
    #    * HTML <img> - the actual image used for displaying and cropping
    #    * HTML <label> and <input type="file> - used for uploading a new
    #                                                              image
    #  * HTML <input type="hidden"> - to remember image path and filename
    #  * JS code - The JS code makes the image a Jcrop widget and
    #              registers an event handler for the <input type="file">
    #              widget. The event handler submits the form so the new
    #              image is sent to the server without the user having
    #              to press the submit button.
    #
    def get_context(self, name, value, attrs):
        context = super(JcropWidget, self).get_context(name, value, attrs)
        context['value'] = value and getattr(value, 'url', None)
        context['preview_height'] = self.preview_height
        context['preview_width'] = self.preview_width
        return context

    def build_attrs(self, attrs):
        attrs = super(JcropWidget, self). build_attrs(attrs)
        attrs.update({"data-{}".format(k): v for k, v in self.jcrop_options.items()})
        attrs['class'] = attrs.get('class', '') + ' jcropped'
        return attrs


class UserDetailsForm(forms.ModelForm):
    x1 = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    y1 = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    x2 = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    y2 = forms.DecimalField(widget=forms.HiddenInput(), required=False)

    class Meta:
        avatar_height = 100
        avatar_width = 100

        model = models.User
        fields = ('first_name', 'last_name', 'sex', 'cell_phone', 'avatar')
        widgets = {
            'sex': floppyforms_widgets.Select(),
            'first_name': floppyforms_widgets.TextInput(),
            'last_name': floppyforms_widgets.TextInput(),
            'cell_phone': floppyforms_widgets.TextInput(),
            'avatar': JcropWidget(
                preview_width=avatar_width, preview_height=avatar_height),
        }

    class Media:
        js = ('js/update_profile.js',)
        css = {
            'all': ("css/update_profile.css",)
        }

    def clean(self):
        """
        instantiate PIL image; raise ValidationError if field contains no image
        """
        cleaned_data = super(UserDetailsForm, self).clean()

        if not self.files.get("avatar"):
            return cleaned_data

        if any(cleaned_data.get(k) is None for k in ['x1', 'y1', 'x2', 'y2']):
            raise forms.ValidationError("please Upload your image again and crop")

        try:
            img = pil_image.open(self.cleaned_data["avatar"])
        except IOError:
            raise forms.ValidationError("Invalid image file")
        img = self.crop(img)
        img = self.resize(img, (self.Meta.avatar_width, self.Meta.avatar_height))

        # saving it to memory
        thumb_io = BytesIO()
        img.save(thumb_io,  self.files['avatar'].content_type.split('/')[-1].upper())

        # generating name for the new file
        new_file_name = (str(self.instance.id) +'_avatar_' +
                        str(int(time.time())) +
                        os.path.splitext(self.instance.avatar.name)[1])

        # creating new InMemoryUploadedFile() based on the modified file
        self.cleaned_data["avatar"] = InMemoryUploadedFile(
            thumb_io, u"avatar", new_file_name,
            cleaned_data['avatar'].content_type, thumb_io.tell(), None)
        return cleaned_data


#     def is_valid(self):
#         """
#         checks if self._errors is empty; if so, self._errors is set to None and
#         full_clean() is called.
#         This is necessary since the base class' is_valid() method does
#         not populate cleaned_data if _errors is an empty ErrorDict (but not 'None').
#         I just failed to work this out by other means...
#         """
#         if self._errors is not None and len(self._errors) == 0:
#             self._errors = None
#             self.full_clean()
#         return super(UserDetailsForm, self).is_valid()

    def crop (self, img):
        """
        crop the image to the user supplied coordinates
        """
        x1=self.cleaned_data['x1']
        x2=self.cleaned_data['x2']
        y1=self.cleaned_data['y1']
        y2=self.cleaned_data['y2']
        return img.crop((x1, y1, x2, y2))

    def resize (self, img, dimensions, maintain_ratio=False):
        """
        resize image to dimensions passed in
        """
        if maintain_ratio:
            img = img.thumbnail(dimensions, pil_image.ANTIALIAS)
        else:
            img = img.resize(dimensions, pil_image.ANTIALIAS)
        return img

    @staticmethod
    def prepare_uploaded_img(files, upload_to, profile, max_display_size=None):
        """
        stores an uploaded image in the proper destination path and
        optionally resizes it so it can be displayed properly.
        Returns path and filename of the new image (without MEDIA_ROOT).

        'upload_to' must be a function reference as expected by Django's
        FileField object, i.e. a function that expects a profile instance
        and a file name and that returns the final path and name for the
        file.
        """
        try:
            upload_file = files[UPLOAD_IMG_ID]
        except MultiValueDictKeyError:
            # files dict does not contain new image
            return None

        # copy image data to final file
        fn = upload_to(profile, upload_file.name)
        pfn = settings.MEDIA_ROOT + fn
        destination = open(pfn, 'wb+')
        for chunk in upload_file.chunks():
            destination.write(chunk)
        destination.close()

        if max_display_size:
            # resize image if larger than specified
            im = pil_image.open(pfn)
            if im.size[0] > max_display_size[0]:
                # image is wider than allowed; resize it
                im = im.resize((max_display_size[0],
                                                im.size[1] * max_display_size[0] / im.size[0]),
                                                pil_image.ANTIALIAS)
            if im.size[1] > max_display_size[1]:
                # image is taller than allowed; resize it
                im = im.resize((im.size[0] * max_display_size[1] / im.size[1],
                                                im.size[1]), pil_image.ANTIALIAS)
            im.save(pfn)

        return fn
