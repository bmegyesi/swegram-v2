
function getQueryStr() {
  var queryStrParts = [];

  $('#loaded_texts_zone input').map(function() {

    if ($( this ).is(':checked')) {
      console.log('checked');
      queryStrParts.push($( this ).attr('data-label') + "=" + $( this ).attr('data-value'));
      console.log(queryStrParts);
    }
  });
  return queryStrParts;
}

function download_stats(general, readability, pos, freq, syntactic){
  return '';

  queryStr = '?';

  if (general === true){
    var table = document.getElementById('table_general');
    for (var r = 1, n = table.rows.length; r < n; r++) {
      queryStr += '&general_' + table.rows[r].cells[0].textContent.replace(/\s/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
    var table = document.getElementById('table_lengths');
    for (var r = 0, n = table.rows.length; r < n; r++) {
      queryStr += '&lengths_' + table.rows[r].cells[0].textContent.replace(/\s+/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
  }

  if (readability === true){
    var table = document.getElementById('table_readability');
    for (var r = 0, n = table.rows.length; r < n; r++) {
      queryStr += '&readability_' + table.rows[r].cells[0].textContent.replace(/\s/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
  }

  if (pos === true){
    var table = document.getElementById('table_pos');
    for (var r = 1, n = table.rows.length; r < n; r++) {
      queryStr += '&pos_' + table.rows[r].cells[0].textContent.replace(/\s/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
  }

  if (freq === true){
    var table = document.getElementById('table_freq');
    for (var r = 1, n = table.rows.length; r < n; r++) {
      queryStr += '&freq_' + table.rows[r].cells[0].textContent.replace(/\s/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
  }

  if (syntactic === true){
    var table = document.getElementById('table_syntactic');
    for (var r = 0, n = table.rows.length; r < n; r++) {
      queryStr += '&syntactic_' + table.rows[r].cells[0].textContent.replace(/\s/g, '') + '=';
      for (var c = 1, m = table.rows[r].cells.length; c < m; c++) {
          queryStr += table.rows[r].cells[c].textContent.replace(/\s/g, '') + '_';
      }
    }
  }
  console.log(queryStr);

  $.get(url_prefix + '/get_stats' + queryStr, function(data) {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('show');

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');

  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });


}

function toggle_metadata(metadata){

  $("input").attr("disabled", true);

  var e = document.getElementById("stats_type_dropdown");
  val = e.options[e.selectedIndex].value;
  $.get(url_prefix + '/update_metadata?meta=' + metadata, function(data) {


  }).fail(function() {
    $("input").attr("disabled", false);
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');

  }).done(function() {

    if (val === 'all_texts'){
      set_loading_all();
      //update_sidebar(false, 'none', false);
    }

    update_everything();
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $(document).ajaxStop(function () {
      $("input").attr("disabled", false);
    });

  });
}

function change_file_state(file_id){
  set_loading_all();
  $("#span_" + file_id).toggleClass("grey_text");
  update_sidebar(false, file_id, false);
}

function change_stats_type(arg){
  $('.general.ui.dimmer').dimmer({closable: false}).dimmer('show');
  var e = document.getElementById("stats_type_dropdown");
  var text_id = e.options[e.selectedIndex].value;
  $.get(url_prefix + '/set_stats_type?id=' + text_id, function(data) {


  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    update_general_stats();
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');

  });

}

function set_freq_limit(type){
  $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('show');
  $.get(url_prefix + '/set_freq_limit?type=' + type, function(data) {

    var source = $('#freq_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#freq_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');
  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}

function get_readability(){
  $('.readability.ui.dimmer').dimmer({closable: false}).dimmer('show');
  $.get(url_prefix + '/readability', function(data) {

    var source = $('#readability_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#readability_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.readability.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');
  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.readability.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}

function get_syntactic(){
  $('.syntactic.ui.dimmer').dimmer({closable:false}).dimmer('show');
  $.get(url_prefix + '/syntactic', function(data){

    var source = $('#syntactic_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#syntactic_zone').html(rendered);

    initialize_semantic();

  }).fail(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.syntactic.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');

  }).done(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.syntactic.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}

function get_morph(){
  $('.morph.ui.dimmer').dimmer({closable:false}).dimmer('show');
  $.get(url_prefix + '/morph', function(data){

    var source = $('#morph_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#morph_zone').html(rendered);
    
    initialize_semantic();
  }).fail(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.morph.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');

  }).done(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.morph.ui.dimmer').dimmer({closable:false}).dimmer('hide');
  });
}

function get_lexical(){
  $('.lexical.ui.dimmer').dimmer({closable:false}).dimmer('show');
  $.get(url_prefix + '/lexical', function(data){

    var source = $('#lexical_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#lexical_zone').html(rendered);
    initialize_semantic();
    
  }).fail(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.lexical.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');

  }).done(function(){
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.lexical.ui.dimmer').dimmer({closable:false}).dimmer('hide');
  });
}

function lengths_words_pos(type){
  queryStr = "?words_pos=" + type;

  $.get(url_prefix + '/lengths' + queryStr, function(data) {

    var source = $('#lengths_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#lengths_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');

  });

}

function update_lengths(type, plusminus){

  queryStr = "?"

  if (type === 'morethan'){
    document.getElementById("morethan_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
    queryStr += 'type=morethan' + '&'
  } else if (type === 'lessthan') {
    document.getElementById("lessthan_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
    queryStr += 'type=lessthan' + '&'
  } else if (type === 'equal') {
    document.getElementById("equal_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
    queryStr += 'type=equal' + '&'
  } else {
    queryStr += 'type=none' + '&'
  }

  if (plusminus === 'plus'){
    queryStr += 'plusminus=plus' + '&'
  } else if (plusminus === 'minus') {
    queryStr += 'plusminus=minus' + '&'
  } else {
    queryStr += 'plusminus=none' + '&'
  }

  $.get(url_prefix + '/lengths' + queryStr, function(data) {

    var source = $('#lengths_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#lengths_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');

  });
}

function set_loading_all(){
  //document.getElementById("morethan_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
  //document.getElementById("lessthan_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
  //document.getElementById("equal_total").innerHTML = '<div class="ui active tiny inline loader"></div>';
  $('#table_general .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_readability .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_freq .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_pos .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_syntactic .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_morph .td_content').html('<div class="ui active tiny inline loader"></div>');
  $('#table_lexical .td_content').html('<div class="ui active tiny inline loader"></div>');
}

function update_general_stats(){
  $('.general.ui.dimmer').dimmer({closable: false}).dimmer('show');
  queryStr = ""

  $.get(url_prefix + '/get_general_stats' + queryStr, function(data) {

    var source = $('#general_stats_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#general_stats_zone').html(rendered);

    var source = $('#n_loaded_texts_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#n_loaded_texts_zone').html(rendered);


    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.general.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');
  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.general.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}

function update_freq_header(){
  queryStr = ""

  $.get(url_prefix + '/get_freq_list' + queryStr, function(data) {

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');

  });
}

function update_freq_pos(pos){
  update_freq(false, pos)
}

function toggle_freq(type){
  update_freq(type, false)
}

function update_freq(type_change=false, toggle_freq_pos=false){
  $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('show');
  //$('#table_freq .td_content').html('<div class="ui active tiny inline loader"></div>');
  queryStr = "?"

  if (type_change != false){
    queryStr += 'type_change=' + type_change + '&'
  }
  if (toggle_freq_pos != false){
    queryStr += 'toggle_freq_pos=' + toggle_freq_pos + '&'
  }

  $.get(url_prefix + '/get_freq_list' + queryStr, function(data) {

    var source = $('#freq_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#freq_zone').html(rendered);

    var source = $('#freq_header_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#freq_header_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');
  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.freq.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });

}

function update_pos_list(){

  $.get(url_prefix + '/pos_stats', function(data) {



  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}

function update_pos(toggle=false){
  $('.pos.ui.dimmer').dimmer({closable: false}).dimmer('show');
  var queryStr = '?'
  //$("input").attr("disabled", true);

  if (toggle != false){
    queryStr += 'toggle=' + toggle + '&'
  }


  $.get(url_prefix + '/pos_stats' + queryStr, function(data) {

    var source = $('#pos_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#pos_zone').html(rendered);

    var source = $('#pos_list_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#pos_list_zone').html(rendered);



  }).fail(function() {
    //$("input").attr("disabled", false);
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.pos.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    console.log('Javascript error');
  }).done(function() {
    //$("input").attr("disabled", false);
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    $('.pos.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  });
}



function update_sidebar(rm=false, file_id="none", update_loaded_texts = true){
  //$('.ui.dimmer').dimmer({closable: false}).dimmer('show');
  var queryStr = "?";

  if (rm != false){
    queryStr += "rm=" + rm + '&';
  }

  if (file_id != "none"){
    queryStr += 'set_state=' + file_id + '&';
  }

  $.get(url_prefix + '/update_sidebar' + queryStr, function(data) {

    var source = $('#text_menu_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#text_menu_zone').html(rendered);

    var source = $('#filter_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#filter_zone').html(rendered);

    if (update_loaded_texts) {
      var source = $('#loaded_texts_template').html();
      var template = Handlebars.compile(source);
      var rendered = template(data);
      $('#loaded_texts_zone').html(rendered);
    }

    var source = $('#metadata_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#metadata_zone').html(rendered);

    initialize_semantic();

  }).fail(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
  console.log('Javascript error');


  }).done(function() {
    $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
    update_everything();
  });
}

function update_everything(){
  //set_loading_all();
  update_lengths();
  update_general_stats();
  //update_pos_list();

  //update_freq_header();
  //update_freq_pos();
  update_freq();
  get_readability();
  get_syntactic();
  get_morph();
  get_lexical();
  update_pos();
  initialize_semantic();

}
