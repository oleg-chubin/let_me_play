$(function(){
    $(".charts-div").map(function(){
        var self = $(this);
        var chart_data = self.find("tbody").find('tr').map(function(){
            return {
                date: $(this).find('td:nth-of-type(1)').html(),
                value: parseFloat($(this).find('td:nth-of-type(2)').html())
            }
        });
        var min_value = chart_data[0].value;
        var max_value = chart_data[0].value;
        for (var i = 0; i < chart_data.length; i++) {
          if (chart_data[i].value < min_value) {min_value = chart_data[i].value;}
          if (chart_data[i].value > max_value) {max_value = chart_data[i].value;}
        }
        self.html('');
        Morris.Line({
          element: this.id,
          data: chart_data,
          xkey: 'date',
          ymin: min_value - (max_value - min_value) / 2 - 1,
          ykeys: ['value'],
          labels: ['date', 'value']
        });
    });
}
)
