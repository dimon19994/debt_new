$("button[name='btn_repay']").click(function() {

    window.location = "new_repay?event_id="+$(this).data('event_id');

});
