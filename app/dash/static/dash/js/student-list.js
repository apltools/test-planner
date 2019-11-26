Handlebars.registerHelper("join", function (context, block) {
    const delimiter = block.hash.delimiter || ", ";
    return context.join(delimiter);
});

function removeTrailingSlash(str) {
    return str.replace(/\/$/, "");
}

function disableCancelConfirmButton(button) {
    button.attr('disabled', true);
    button.html("<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span>\n" +
        "  <span class=\"sr-only\">Loading...</span>");
}

function enableCancelConfirmButton(button) {
    button.removeAttr('disabled');
    button.html('Ja');
}

function studentListWaitingSpinner() {
    $('#student-list').html("<div class=\"d-flex justify-content-center\">\n" +
        "  <div class=\"spinner-border\" role=\"status\">\n" +
        "    <span class=\"sr-only\">Loading...</span>\n" +
        "  </div>\n" +
        "</div>");
}

function prepareModal(cancelVars) {
    const modalBody = $('.modal-body');
    modalBody.html("");

    const request = $.get(cancelModalTemplateUrl);
    request.done(function (data) {
        const cancelTemplate = Handlebars.compile(data);
        modalBody.html(cancelTemplate(cancelVars));
    });
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

window.history.replaceState(null, null, removeTrailingSlash(location.pathname) + location.hash);

$(function () {
    // Load appointment template
    let request = $.get(appointmentTemplateUrl);
    request.done(function (data) {
        const template = Handlebars.compile(data);

        // Bind on-click to menu pills
        $('a[data-toggle="pill"]').on("shown.bs.tab", function () {
            studentListWaitingSpinner();
            const tmId = $(this).data('tm-id');

            location.hash = `date-${tmId}`;

            // Get appointments
            let request = $.getJSON(`/api/appointments/${tmId}`);
            request.done(function (data) {
                $('#student-list').html(template(data));

                // Bind delete function to appointments
                $('.cancel-inline').on('click', function () {
                    const button = $(this);
                    $('#modalCancelButton').data('app-id', button.data('app-id'));

                    const cancelVars = {
                        time: button.parent().parent().siblings().find('.time').html(),
                        name: button.parent().find('.name').html()
                    };

                    prepareModal(cancelVars);

                    $('#cancelConfirmModal').modal('show');
                });
            });
        });

        const hashTab = $(`a[href="${location.hash}"]`);

        if (hashTab.length) {
            hashTab.tab('show')
        } else {
            $('#dateTabList a:first-child').tab('show')
        }
    });

    $('#modalCancelButton').on('click', function () {
        const button = $(this);
        disableCancelConfirmButton(button);
        const appId = button.data('app-id');

        let request = $.post(cancelAppointmentUrl, {appId: button.data('app-id')});
        request.done(function (data) {
            if (data) {
                $(`li[data-app-id=${appId}]`).remove();
            }

            $('#cancelConfirmModal').modal('hide');
            enableCancelConfirmButton(button);
        });

    });
});