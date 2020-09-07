$(document).ready(function () {
    $(".btn-primary:first").click(function () {
        var a = Number($(".form-group td:nth-child(2) input")[$(".form-group td:nth-child(2) input").length - 1].id.split("-")[1]);
        var count = Number($(".form-group td:nth-child(2) input").length);
        var select = $(".form-group td:nth-child(3n) select")[0].innerHTML;

        $(".form-group:eq(" + (count + 1) + ")").before("" +
            "<div class=\"form-group\">\n" +
            "                        <table>\n" +
            "                            <tbody><tr>\n" +
            "                                <td>\n" +
            "                                    <label for=\"check_item-" + (a + 1) + "\">Продукт: </label>\n" +
            "                                </td>\n" +
            "                                <td>\n" +
            "                                    <label for=\"item_cost-" + (a + 1) + "\">Цена продукта: </label>\n" +
            "                                </td>\n" +
            "                                <td>\n" +
            "                                    <label for=\"item_type-" + (a + 1) + "\">Тип продукта: </label>\n" +
            "                                </td>\n" +
            "                            </tr>\n" +
            "                            <tr>\n" +
            "                                <td>\n" +
            "                                    <input id=\"item_id-" + (a + 1) + "\" name=\"item_id-" + (a + 1) + "\" type=\"hidden\" value=\"\">\n" +
            "                                    <input class=\"form-control\" id=\"check_item-" + (a + 1) + "\" name=\"check_item-" + (a + 1) + "\" required=\"\" type=\"text\" value=\"\">\n" +
            "                                    \n" +
            "                                </td>\n" +
            "                                <td>\n" +
            "                                    <input class=\"form-control\" id=\"item_cost-" + (a + 1) + "\" name=\"item_cost-" + (a + 1) + "\" required=\"\" type=\"text\" value=\"\">\n" +
            "                                    \n" +
            "                                </td>\n" +
            "                                <td>\n" +
            "                                    <select class=\"form-control\" id=\"item_type-" + (a + 1) + "\" name=\"item_type-" + (a + 1) + "\" required=\"\">" + select + "</select>\n" +
            "                                </td>\n" +
            "                               <td>\n" +
            "                                   <button type=\"button\" class=\"btn btn-danger item_delete\" id=\"item_delete-" + (a + 1) + "\">Удалить</button>\n" +
            "                              </td>\n" +
            "                            </tr>\n" +
            "                        </tbody></table>\n" +
            "                    </div>" +
            "");
    });


    $(".btn-primary:last").click(function () {
        var a = Number(($(".form-group td .pay:eq(-1)")[0].id).split("-")[1]);
        var select = $("#check_pay-0")[0].innerHTML;
        $(".form-group:eq(-1)").before("" +
            "<div class=\"form-group\">\n" +
            "                        <table>\n" +
            "                            <tbody><tr>\n" +
            "                                <td>\n" +
            "                                    <label for=\"check_sum-" + (a + 1) + "\">Сумма: </label>\n" +
            "                                </td>\n" +
            "                                <td>\n" +
            "                                    <label for=\"check_pay-" + (a + 1) + "\">Плательщик: </label>\n" +
            "                                </td>\n" +
            "                            </tr>\n" +
            "                            <tr>\n" +
            "                               <td>\n" +
            "                                   <input class=\"form-control pay\" id=\"check_sum-" + (a + 1) + "\" name=\"check_sum-" + (a + 1) + "\" required=\"\" type=\"text\" value=\"\">\n" +
            "                                   \n" +
            "                               </td>\n" +
            "                               <td>\n" +
            "                                   <select class=\"form-control\" id=\"check_pay-" + (a + 1) + "\" name=\"check_pay-" + (a + 1) + "\">" + select + "</select>\n" +
            "                               </td>\n" +
            "                               <td>\n" +
            "                                   <button type=\"button\" class=\"btn btn-danger pay_delete\" id=\"pay_delete-" + (a + 1) + "\">Удалить</button>\n" +
            "                               </td>\n" +
            "                            </tr>\n" +
            "                        </tbody></table>\n" +
            "                    </div>" +
            "");
    });

    $("form").change(function (event) {
        if (event.target.id.split("-")[0] == "item_cost" || event.target.id == "check_sale" || event.target.id.split("-")[0] == "check_sum") {
            var sum = 0;
            for (let i = 0; i < $(".form-group td:nth-child(2) input").length; i++) {
                sum += Number($(".form-group td:nth-child(2) input")[i].value)
            }
            for (let i = 1; i < $(".form-group td .pay").length; i++) {
                sum -= Number($(".form-group td .pay")[i].value)
            }

            $(".form-group td .pay")[0].value = (sum + Number($("#check_sale")[0].value)).toFixed(2);
        }
    });

    $("form").click(function (event) {
        if (event.target.id.split("-")[0] == "item_delete" && $(".item_delete").length > 1) {
            event.target.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
        }
    })

    $("form").click(function (event) {
        if (event.target.id.split("-")[0] == "pay_delete") {
            event.target.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
        }
    })

    $("form").click(function (event) {
        if (event.target.id.split("-")[0] == "item_delete" || event.target.id.split("-")[0] == "pay_delete") {
            var sum = 0;
            for (let i = 0; i < $(".form-group td:nth-child(2) input").length; i++) {
                sum += Number($(".form-group td:nth-child(2) input")[i].value)
            }
            for (let i = 1; i < $(".form-group td .pay").length; i++) {
                sum -= Number($(".form-group td .pay")[i].value)
            }

            $(".form-group td .pay")[0].value = (sum + Number($("#check_sale")[0].value)).toFixed(2);
        }
    });
});

