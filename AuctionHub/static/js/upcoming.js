$('[data-countdown]').each(function(){
    var $deadline = new Date($(this).data('countdown')).getTime();

    var $dataDays = $(this).children('[data-days]');
    var $dataHours = $(this).children('[data-hours]');
    var $dataMinuts = $(this).children('[data-minuts]');
    var $dataSeconds = $(this).children('[data-seconds]');

    var x = setInterval(function(){

        var now = new Date().getTime();
        var t = $deadline - now;

        var days = Math.floor(t/(1000*60*60*24));
        var hours = Math.floor(t%(1000*60*60*24) / (1000*60*60));
        var minuts = Math.floor(t%(1000*60*60) / (1000*60));
        var seconds = Math.floor(t%(1000*60) / (1000));

        if( days < 10 ){
            days = '0'+days;
        }

        if( hours < 10 ){
            hours = '0'+hours;
        }

        if( minuts < 10 ){
            minuts = '0'+minuts;
        }

        if( seconds < 10 ){
            seconds = '0'+seconds;
        }

        $dataDays.html(days);
        $dataHours.html(hours);
        $dataMinuts.html(minuts);
        $dataSeconds.html(seconds);


        if( t <= 0 ){
            clearInterval(x);

            $dataDays.html('00');
            $dataHours.html('00');
            $dataMinuts.html('00');
            $dataSeconds.html('00');

        }
    },1000);
})