//
// MegaQC: filter_samples.js
// ---------------------------
// Used by pages loading the Filter Samples modal dialogue
// to create new sample filter sets.

// To be set in the page using Python vars:
//   window.token
//   window.report_fields
//   window.sample_fields
//   window.num_matching_samples

$(function () {

    function validateForm() {
        var formValid = $('#threshold_meta')[0].reportValidity();

        var filterValid = window.active_filters.length > 0;

        if (!filterValid)
            toastr.error('Please add one or more filters');

        return filterValid && formValid;
    }

    // Submit the new threshold
    $('#submit-threshold').click(function (e) {
        e.preventDefault();
        $('#sample-filters-save input').removeClass('is-invalid');

        // Cancel any running ajax calls
        if (window.ajax_update !== false) {
            window.ajax_update.abort();
        }

        // Stop submission if our data isn't valid
        if (!validateForm())
            return;

        // Call the AJAX endpoint to save the filters
        var new_filters = {
            'filters': window.active_filters,
            'meta': $('#threshold_meta')
                .serializeArray()
                .reduce(function (acc, curr) {
                    acc[curr.name] = curr.value;
                    return acc;
                }, {})
        };
        window.ajax_update = $.ajax({
            url: '/api/save_alert_threshold',
            type: 'post',
            data: JSON.stringify(new_filters),
            headers: {access_token: window.token},
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function (data) {
                console.log(data);
                if (data['success']) {
                    new_filters['filter_id'] = data['filter_id'];
                    $('#create_threshold_modal').modal('hide');
                    toastr.success('Alert threshold created successfully!');
                    $('#create_threshold_modal').html(window.original_filtermodal);
                    window.setTimeout(function () {
                        location.reload()
                    }, 2000);
                }
                // AJAX data['success'] was false
                else {
                    console.log(data);
                    toastr.error('There was an error saving the sample filters:<br><em>' + data['message'] + '</em>');
                }
            },
            error: function (data) {
                toastr.error('There was an error saving the sample filters.');
            }
        });
    });
});
