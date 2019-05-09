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
    // Add new filter GROUP button
    $('body').on('click', '.new-filter-group-add-btn', function (e) {
        new_group_card = $('.new-filter-group-card').first().clone();
        var new_idx = $('.new-filter-group-card').length + 1;
        new_group_card.find('.card-header').html(
            '<button class="new-filter-group-delete btn btn-sm btn-outline-secondary float-right">Delete</button>' +
            'Filter Group ' + new_idx);
        new_group_card.find('tbody').html('');
        new_group_card.find('.new-filter-add').prop('disabled', true);
        new_group_card.find('.new-filter-key').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        new_group_card.find('.new-filter-cmp').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
        new_group_card.find('.new-filter-value').html('<input disabled class="form-control" type="text" placeholder="[ please select a filter type ]">');
        new_group_card.hide().insertBefore($(this)).slideDown();
    });

    // Delete new filter GROUP
    $('body').on('click', '.new-filter-group-delete', function (e) {
        $(this).closest('.new-filter-group-card').slideUp(function () {
            $(this).remove();
        });
    });

    // When the builder is updated, send an AJAX request to fetch the list of samples
    $('.new-filter-group-card').on('builder:updated', function () {
        // Call the AJAX endpoint to update the page
        window.ajax_update = $.ajax({
            url: '/api/report_filter_fields',
            type: 'post',
            data: JSON.stringify({'filters': window.active_filters}),
            headers: {access_token: window.token},
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function (data) {
                if (data['success']) {

                    // Update the Javascript variables
                    window.num_matching_samples = data['num_samples'];
                    window.filter_error = false;

                    // Update number of matching samples
                    $('.newfilter_num_filtered_samples').text(data['num_samples'] + ' samples');
                    $('.newfilter_num_filtered_samples').removeClass('badge-danger badge-success badge-warning');
                    if (parseInt(data['num_samples']) == 0) {
                        $('.newfilter_num_filtered_samples').addClass('badge-danger');
                    } else if (parseInt(data['num_samples']) > 100) {
                        $('.newfilter_num_filtered_samples').addClass('badge-warning');
                    } else {
                        $('.newfilter_num_filtered_samples').addClass('badge-success');
                    }

                    // Hide the loading spinner
                    $('.loading-spinner').hide();

                    // AJAX data['success'] was false
                } else {
                    console.log(data);
                    toastr.error('There was an error applying the sample filters: ' + data['message']);
                    $('.newfilter_num_filtered_samples').text('Error applying filters').removeClass('badge-success badge-warning').addClass('badge-danger');
                    $('.loading-spinner').hide();
                    window.num_matching_samples = 0;
                    window.filter_error = true;
                }
            },
            error: function (data) {
                toastr.error('There was an error applying the sample filters.');
                $('.newfilter_num_filtered_samples').text('Error applying filters').removeClass('badge-success badge-warning').addClass('badge-danger');
                $('.loading-spinner').hide();
                window.num_matching_samples = 0;
                window.filter_error = true;
            }
        });
    });

    // New group of filters
    $('#filters_set').on('focus', function () {
        filters_set_previous = this.value;
    }).change(function (e) {
        if ($(this).val() == '') {
            var fs_name = prompt("Please enter a name for the new filter set:");
            if (fs_name != null) {
                $('<option>' + fs_name + '</option>').appendTo($('#filters_set')).prop('selected', true);
                filters_set_previous = fs_name;
            } else {
                // Cancelled - go back to previous value
                $('#filters_set').val(filters_set_previous);
            }
        } else {
            filters_set_previous = $(this).val();
        }
    });

    // Save report filters
    $('#sample-filters-save').submit(function (e) {
        e.preventDefault();
        $('#sample-filters-save input').removeClass('is-invalid')
        // Check that there wasn't an error with the filters
        if (window.filter_error) {
            toastr.error('There was an error applying your filters.');
            return false;
        }
        // Check that there are some filters to save
        if (window.active_filters.length == 0) {
            toastr.error('You must add some filters before saving.');
            return false;
        }
        // Check that we have a name
        if ($('#filters_name').val().trim().length == 0) {
            toastr.error('Please enter a name for these filters.');
            $('#filters_name').addClass('is-invalid').focus();
            return false;
        }
        if ($('#filters_set').val().trim().length == 0) {
            toastr.error('Please choose a filter group for these filters.');
            $('#filters_set').addClass('is-invalid').focus();
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
            url: '/api/save_filters',
            type: 'post',
            data: JSON.stringify(new_filters),
            headers: {access_token: window.token},
            dataType: 'json',
            contentType: 'application/json; charset=UTF-8',
            success: function (data) {
                console.log(data);
                if (data['success']) {
                    new_filters['filter_id'] = data['filter_id'];
                    $(document).trigger('sample-filter-saved', new_filters);
                    toastr.success(data['message']);
                    $('#create_filter_modal').html(window.original_filtermodal);
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

    // New sample filter set saved
    $(document).on('sample-filter-saved', function (e, fs) {
        // Hide the modal window
        $('#create_filter_modal').modal('hide');
        // Select the correct sample filter group
        $('#sample-filter-group-select .nav-link').removeClass('active');
        var sfg = $('#sample-filter-group-select .nav-link').filter(function (index) {
            return $(this).text() === fs['meta']['set'];
        });
        $('.sample-filters-group').hide();
        if (sfg.length > 0) {
            sfg.addClass('active');
            $('.sample-filters-group[data-filtergroup="' + fs['meta']['set'] + '"]').show();
        } else {
            var idx = $('#sample-filter-group-select .nav-link').length + 1;
            $('#sample-filter-group-select').append('<a class="nav-link active" href="#sample_filter_group_' + idx + '">' + fs['meta']['set'] + '</a>');
            $('#sample-filter-groups').append('<div class="sample-filters-group" id="sample_filter_group_' + idx + '" data-filtergroup="' + fs['meta']['set'] + '"><div class="list-group"></div></div>');
        }
        // Insert the new filters and select them
        $('.sample-filter-btn').removeClass('active');
        $('.sample-filters-group[data-filtergroup="' + fs['meta']['set'] + '"] .list-group').append(
            '<button type="button" class="sample-filter-btn list-group-item list-group-item-action active" data-filterid="' + fs['filter_id'] + '">' + fs['meta']['name'] + '</button>'
        );
        $(document).trigger('sample-filter-added');
    });

    // Change visible sample groups
    $('#sample-filter-group-select').on('click', 'a', function (e) {
        e.preventDefault();
        $('#sample-filter-group-select a').removeClass('active');
        $(this).addClass('active');
        var target = $(this).attr('href');
        $('.sample-filters-group:visible').fadeOut(100, function () {
            $(target).fadeIn(100);
        });
    });

    // Sample filter clicked
    $('#sample-filter-groups').on('click', '.sample-filter-btn', function (e) {
        e.preventDefault();
        $('.sample-filter-btn').removeClass('active');
        $(this).addClass('active');
        $(document).trigger('sample-filter-clicked');
    });

});
