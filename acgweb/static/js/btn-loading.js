$(".btn[data-loading-text]").click(function(e) {
    var $btn = $(this);
    if ($btn.attr('disabled')) {
        e.preventDefault();
    }
    $btn.button('loading').attr('disabled',"true");
});