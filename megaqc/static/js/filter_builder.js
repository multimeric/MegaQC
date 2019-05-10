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
window.ajax_update = false;
window.original_filtermodal = false;
// Initialise the chosen select boxes
$('.form-control-chosen-required').chosen({'disable_search_threshold': 10});

// Save a copy of the filter modal so that we can reset it easily later
window.original_filtermodal = $('#create_filter_modal').html();

// Add new filter - Type dropdown
$('body').on('change', '.new-filter-type select', function(e){
    // Reset downstream selectors
    var button_e = $(this).closest('tr').find('.new-filter-add');
    var key_e = $(this).closest('tr').find('.new-filter-key');
    var cmp_e = $(this).closest('tr').find('.new-filter-cmp');
    var val_e = $(this).closest('tr').find('.new-filter-value');
    button_e.prop('disabled', false);
    key_e.html('<select class="form-control form-control-chosen-required" required data-placeholder="[ please select key ]"><option></option></select>');
    cmp_e.html('<select class="form-control form-control-chosen-required" required data-placeholder="[ please select comparison ]"><option></option></select>');
    val_e.html('<input class="form-control" type="text">');
    switch($(this).val()) {
        case 'timedelta':
            key_e.html('<input type="text" readonly class="form-control-plaintext" value="Dynamic dates">');
            cmp_e.find('select').html('<option value="le">Within dates</option><option value="gt">Except dates</option>');
            val_e.find('input').attr('placeholder', 'Number of days');
            break;
        case 'daterange':
            key_e.html('<input type="text" readonly class="form-control-plaintext" value="Specific dates">');
            cmp_e.find('select').html('<option value="le">Within dates</option><option value="gt">Except dates</option>');
            val_e.html('<input class="form-control" type="date"> <input class="form-control" type="date">')
            break;
        case 'reportmeta':
            $.each(window.report_fields, function(idx, field){
                key_e.find('select').append('<option value="'+field+'">'+field+'</option>');
            });
            $.each(window.data_cmp, function(val, txt){
                cmp_e.find('select').append('<option value="'+val+'">'+txt+'</option>');
            });
            break;
        case 'samplemeta':
            $.each(window.sample_fields, function(idx, field){
                key_e.find('select').append('<option value="'+field['key']+'">'+field['nicename']+'</option>');
            });
            $.each(window.data_cmp, function(val, txt){
                cmp_e.find('select').append('<option value="'+val+'">'+txt+'</option>');
            });
            break;
        default:
            button_e.prop('disabled', true);
            key_e.find('select').prop('disabled', true).html('<option value="">[ please select a filter type ]<option>');
            cmp_e.find('select').prop('disabled', true).html('<option value="">[ please select a filter type ]<option>');
            val_e.find('input').prop('disabled', true).attr('placeholder', '[ please select a filter type ]');
            break;
    }
    $('.form-control-chosen-required').trigger("chosen:updated");
    $('.form-control-chosen-required').chosen({'disable_search_threshold': 10});
});

// Add new filter ROW
$('body').on('click', '.new-filter-add', function(e){
    add_filter_row($(this));
});
// Pressing enter on a value input
$('body').on('keyup', '.new-filter-value input', function (e) {
    if (e.keyCode == 13) {
        add_filter_row($(this));
    }
});

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

function add_filter_row(el){
    var ftype_val = el.closest('tr').find('.new-filter-type select').val();
    var fkey_val = el.closest('tr').find('.new-filter-key select').val();
    var fcmp_val = el.closest('tr').find('.new-filter-cmp select').val();
    var fvalue_val = el.closest('tr').find('.new-filter-value input').val();
    var ftype_txt = el.closest('tr').find('.new-filter-type option:selected').text();
    var fkey_txt = el.closest('tr').find('.new-filter-key option:selected').text();
    var fcmp_txt = el.closest('tr').find('.new-filter-cmp option:selected').text();
    if(fkey_val == undefined){
        fkey_val = fkey_txt = el.closest('tr').find('.new-filter-key input').val();
    }
    // Check that we have everything that we need
    if(ftype_val.trim() == ''){ toastr.error('Please select a filter type'); return;  }
    if(fkey_val.trim() == ''){ toastr.error('Please select a filter key'); return;  }
    if(fcmp_val.trim() == ''){ toastr.error('Please select a comparison type'); return;  }
    if(fvalue_val.trim() == ''){ toastr.error('Please select a filter value'); return;  }

    new_filter_row = $('<tr>' +
        '<td><div class="new-filter-type" data-value="'+ftype_val+'">'+ftype_txt+'</div></td>' +
        '<td><div class="new-filter-key" data-value="'+fkey_val+'">'+fkey_txt+'</div></td>' +
        '<td><div class="new-filter-cmp" data-value="'+fcmp_val+'">'+fcmp_txt+'</div></td>' +
        '<td><div class="new-filter-value" data-value="'+fvalue_val+'"><code>'+fvalue_val+'</code></div></td>' +
        '<td><div>' +
        '<button class="new-filter-delete btn btn-sm btn-outline-danger">' +
        '<i class="fa fa-trash" aria-hidden="true"></i> Delete' +
        '</button>' +
        '</div></td>' +
        '</tr>');
    // Animate table row slidedown - https://stackoverflow.com/a/3410943/713980
    new_filter_row.appendTo( el.closest('table').find('tbody') )
        .find('td div').hide().slideDown();
    // Reset new filter row
    el.closest('tr').find('.new-filter-type select').val('');
    el.closest('tr').find('.new-filter-key').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
    el.closest('tr').find('.new-filter-cmp').html('<select disabled class="form-control"><option value="">[ please select a filter type ]<option></select>');
    el.closest('tr').find('.new-filter-value').html('<input disabled class="form-control" type="text" placeholder="[ please select a filter type ]">');
    el.closest('tr').find('.new-filter-add').prop('disabled', true);

    // Give specific users of this component to listen for changes
    $('.new-filter-group-card').trigger('builder:updated');

    update_filters();
}

// Update filters
function update_filters(){
    $('.loading-spinner').show();
    // Cancel any running ajax calls
    if(window.ajax_update !== false){
        window.ajax_update.abort();
    }
    // Build active_filters object from tables
    window.active_filters = [];
    $('.filter-group-table').each(function(){
        var t_filters = [];
        $(this).find('tbody tr').each(function(){
            var filter = {
                'type': $(this).find('.new-filter-type').data('value'),
                'key': $(this).find('.new-filter-key').data('value'),
                'cmp': $(this).find('.new-filter-cmp').data('value'),
                'value': $(this).find('.new-filter-value').data('value')
            };
            var fsection = $(this).find('.new-filter-key').data('section');
            if( fsection !== undefined ){
                filter['section'] = fsection;
            }
            t_filters.push(filter);
        });
        window.active_filters.push(t_filters);
    });
}

// Delete new filter ROW
$('body').on('click', '.new-filter-delete', function(e){
    $(this).closest('tr').find('td div').slideUp(function(){
        $(this).closest('tr').remove();
    });
});
