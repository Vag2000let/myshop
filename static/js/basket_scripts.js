window.onload = function () {
    console.log('DOM LOADED');
    $(".userbasket").on('change',
        'input[type="number"]',
        function (event) {
            // console.log(event.target);
            // console.log(event.target.name);
            // console.log(event.target.value);
            $.ajax({
                url: "/basket/update/" + event.target.name + "/" + event.target.value + "/",
                success: function (data) {
                    // console.log(data);
                    $('.userbasket').html(data.result);
                }
            });
        })
};