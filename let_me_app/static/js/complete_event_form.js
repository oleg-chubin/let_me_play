$(function(){
    $('form input[type=checkbox]').change(
        function(){
            var was_checked = !document.getElementById(this.id).checked;
            $(this).closest('.input-group').find('input[type=number]').attr('disabled', was_checked)
        }
    );
})
