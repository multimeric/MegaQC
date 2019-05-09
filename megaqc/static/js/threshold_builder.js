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

window.data_cmp = {
    "in": "Contains string",
    "not in": "Does not contain string",
    "eq": "(=) Equal to",
    "ne": "(!=) Not equal to",
    "le": "(&le;) Less than or equal to",
    "lt": "(&lt;) Less than",
    "ge": "(&ge;) Greater than or equal to",
    "gt": "(&gt;) Greater than"
};
window.active_filters = [];
window.filter_error = false;
window.ajax_update = false;
window.original_filtermodal = false;
$(function () {
// Save report filters
    $('#submit-threshold').click(function (e) {
        e.preventDefault();
        $('#sample-filters-save input').removeClass('is-invalid');
        // Check that there wasn't an error with the filters
        if (window.filter_error) {
            toastr.error('There was an error applying your filters.');
            return false;
        }

        // Cancel any running ajax calls
        if (window.ajax_update !== false) {
            window.ajax_update.abort();
        }
        // Call the AJAX endpoint to save the filters
        var new_filters = {
            'filters': window.active_filters,
            'meta': {
                'name': $('#filters_name').val(),
                'set': $('#filters_set').val(),
                'is_public': ($('#filters_visiblity').val() == 'Everyone')
            }
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
