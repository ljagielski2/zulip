var settings_profile_fields = (function () {

var exports = {};

var meta = {
    loaded: false,
};

var order = [];

exports.field_type_id_to_string = function (type_id) {
    var name = _.find(page_params.custom_profile_field_types, function (type) {
        return type[0] === type_id;
    })[1];
    return name;
};

function delete_profile_field(e) {
    e.preventDefault();
    e.stopPropagation();

    settings_ui.do_settings_change(
        channel.del,
        "/json/realm/profile_fields/" + encodeURIComponent($(this).attr('data-profile-field-id')),
        {}, $('#admin-profile-field-status').expectOne());
}

function read_field_data_from_form(selector) {
    var field_data = {};
    var field_order = 1;
    selector.each(function () {
        var text = $(this).find("input")[0].value;
        field_data[field_order - 1] = {text: text, order: field_order.toString()};
        field_order += 1;
    });

    return field_data;
}

function update_choice_delete_btn(container, display_flag) {
    var no_of_choice_row = container.find(".choice-row").length;

    // Disable delete button if there only one choice row
    // Enable choice delete button more one than once choice
    if (no_of_choice_row === 1) {
        if (display_flag === true) {
            container.find(".choice-row .delete-choice").show();
        } else {
            container.find(".choice-row .delete-choice").hide();
        }
    }
}

function create_choice_row(container) {
    var context = {};
    var row = templates.render("profile-field-choice", context);
    $(container).append(row);
}

function clear_form_data() {
    $("#profile_field_name").val("");
    $("#profile_field_hint").val("");
    // Set default in field type dropdown
    $("#profile_field_type").val("1");
    // Clear data from choice field form
    $("#profile_field_choices").html("");
    create_choice_row($("#profile_field_choices"));
    update_choice_delete_btn($("#profile_field_choices"), false);
    $("#profile_field_choices_row").hide();
}

function create_profile_field(e) {
    e.preventDefault();
    e.stopPropagation();

    var selector = $('.admin-profile-field-form div.choice-row');
    var field_data = {};

    if ($('#profile_field_type').val() === '3') {
        // Only read choice data if we are creating a choice field.
        field_data = read_field_data_from_form(selector);
    }

    var opts = {
        success_continuation: clear_form_data,
    };
    var form_data = {
        name: $("#profile_field_name").val(),
        field_type: $("#profile_field_type").val(),
        hint: $("#profile_field_hint").val(),
        field_data: JSON.stringify(field_data),
    };

    settings_ui.do_settings_change(channel.post, "/json/realm/profile_fields", form_data,
                                   $('#admin-profile-field-status').expectOne(), opts);
}

function add_choice_row(e) {
    update_choice_delete_btn($(e.delegateTarget).parent(), true);
    var choices_div = e.delegateTarget;
    create_choice_row(choices_div);
}

function delete_choice_row(e) {
    var row = $(e.currentTarget).parent();
    var container = row.parent();
    row.remove();
    update_choice_delete_btn(container, false);
}

function get_profile_field_info(id) {
    var info = {};
    info.row = $("tr.profile-field-row[data-profile-field-id='" + id + "']");
    info.form = $("tr.profile-field-form[data-profile-field-id='" + id + "']");
    return info;
}

function get_profile_field(id) {
    var all_custom_fields = page_params.custom_profile_fields;
    var field;
    for (var i = 0; i < all_custom_fields.length; i += 1) {
        if (all_custom_fields[i].id === id) {
            field = all_custom_fields[i];
            break;
        }
    }
    return field;
}

exports.parse_field_choices_from_field_data = function (field_data) {
    var choices = [];
    _.each(field_data, function (choice, value) {
        choices.push({
            value: value,
            text: choice.text,
            order: choice.order,
        });
    });

    return choices;
};

function open_edit_form(e) {
    var field_id = $(e.currentTarget).attr("data-profile-field-id");
    var profile_field = get_profile_field_info(field_id);

    profile_field.row.hide();
    profile_field.form.show();
    var field = get_profile_field(parseInt(field_id,10));
    // Set initial value in edit form
    profile_field.form.find('input[name=name]').val(field.name);
    profile_field.form.find('input[name=hint]').val(field.hint);

    if (exports.field_type_id_to_string(field.type) === "Choice") {
        // Re-render field choices in edit form to load initial choice data
        var choice_list = profile_field.form.find('.edit_profile_field_choices_container');
        choice_list.off();
        choice_list.html("");

        var field_data = {};
        if (field.field_data !== "") {
            field_data = JSON.parse(field.field_data);
        }
        var choices_data = exports.parse_field_choices_from_field_data(field_data);

        _.each(choices_data, function (choice) {
            choice_list.append(
                templates.render("profile-field-choice", {
                    text: choice.text,
                })
            );
        });

        update_choice_delete_btn(choice_list, false);
        Sortable.create(choice_list[0], {
            onUpdate: function () {},
        });
    }

    profile_field.form.find('.reset').on("click", function () {
        profile_field.form.hide();
        profile_field.row.show();
    });

    profile_field.form.find('.submit').on("click", function () {
        e.preventDefault();
        e.stopPropagation();

        var profile_field_status = $('#admin-profile-field-status').expectOne();

        // For some reason jQuery's serialize() is not working with
        // channel.patch even though it is supported by $.ajax.
        var data = {};
        data.name = profile_field.form.find('input[name=name]').val();
        data.hint = profile_field.form.find('input[name=hint]').val();
        var selector = profile_field.form.find('div.choice-row');
        data.field_data = JSON.stringify(read_field_data_from_form(selector));

        settings_ui.do_settings_change(channel.patch, "/json/realm/profile_fields/" + field_id,
                                       data, profile_field_status);
    });

    profile_field.form.find(".edit_profile_field_choices_container").on("click", "button.add-choice", add_choice_row);
    profile_field.form.find(".edit_profile_field_choices_container").on("click", "button.delete-choice", delete_choice_row);
}

exports.reset = function () {
    meta.loaded = false;
};

function update_field_order() {
    order = [];
    $('.profile-field-row').each(function () {
        order.push(parseInt($(this).attr('data-profile-field-id'), 10));
    });
    settings_ui.do_settings_change(channel.patch, "/json/realm/profile_fields",
                                   {order: JSON.stringify(order)},
                                   $('#admin-profile-field-status').expectOne());
}

exports.populate_profile_fields = function (profile_fields_data) {
    if (!meta.loaded) {
        // If outside callers call us when we're not loaded, just
        // exit and we'll draw the widgets again during set_up().
        return;
    }
    exports.do_populate_profile_fields(profile_fields_data);
};

exports.do_populate_profile_fields = function (profile_fields_data) {
    // We should only call this internally or from tests.
    var profile_fields_table = $("#admin_profile_fields_table").expectOne();

    profile_fields_table.find("tr.profile-field-row").remove();  // Clear all rows.
    profile_fields_table.find("tr.profile-field-form").remove();  // Clear all rows.
    order = [];
    _.each(profile_fields_data, function (profile_field) {
        order.push(profile_field.id);
        var field_data = {};
        if (profile_field.field_data !== "") {
            field_data = JSON.parse(profile_field.field_data);
        }
        var choices = exports.parse_field_choices_from_field_data(field_data);
        var is_choice_field = false;

        if (profile_field.type === 3) {
            is_choice_field = true;
        }

        profile_fields_table.append(
            templates.render(
                "admin_profile_field_list", {
                    profile_field: {
                        id: profile_field.id,
                        name: profile_field.name,
                        hint: profile_field.hint,
                        type: exports.field_type_id_to_string(profile_field.type),
                        choices: choices,
                        is_choice_field: is_choice_field,
                    },
                    can_modify: page_params.is_admin,
                }
            )
        );
    });
    if (page_params.is_admin) {
        var field_list = $("#admin_profile_fields_table")[0];
        Sortable.create(field_list, {
            onUpdate: update_field_order,
        });
    }
    loading.destroy_indicator($('#admin_page_profile_fields_loading_indicator'));
};

function set_up_choices_field() {
    create_choice_row('#profile_field_choices');
    update_choice_delete_btn($("#profile_field_choices"), false);

    var choice_list = $("#profile_field_choices")[0];
    Sortable.create(choice_list, {
        onUpdate: function () {},
    });

    if ($('#profile_field_type').val() !== '3') {
        // If 'Choice' type is already selected, show choice row.
        $("#profile_field_choices_row").hide();
    }

    $('#profile_field_type').on('change', function (e) {
        if ($(e.target).val() === '3') {
            $("#profile_field_choices_row").show();
        } else {
            $("#profile_field_choices_row").hide();
        }
    });

    $("#profile_field_choices").on("click", "button.add-choice", add_choice_row);
    $("#profile_field_choices").on("click", "button.delete-choice", delete_choice_row);
}

exports.set_up = function () {

    // create loading indicators
    loading.make_indicator($('#admin_page_profile_fields_loading_indicator'));
    // Populate profile_fields table
    exports.do_populate_profile_fields(page_params.custom_profile_fields);
    meta.loaded = true;

    $('#admin_profile_fields_table').on('click', '.delete', delete_profile_field);
    $("#profile-field-settings").on("click", "#add-custom-profile-field-btn", create_profile_field);
    $("#admin_profile_fields_table").on("click", ".open-edit-form", open_edit_form);
    set_up_choices_field();
};

return exports;
}());

if (typeof module !== 'undefined') {
    module.exports = settings_profile_fields;
}
window.settings_profile_fields = settings_profile_fields;
