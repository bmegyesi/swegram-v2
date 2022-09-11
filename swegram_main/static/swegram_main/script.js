
function openTab(tab){
  $('.left_col').css('display', 'none');
  $('#' + tab).css('display', 'inline-block');
}

function makeActive(button){
  $('.item').removeClass('active');
  button.classList.add('active');
}

document.getElementById('pasted_text').onkeyup = function () {
    if ($('#pasted_text').val().length === 0){
      $('#annotate_submit_label').addClass('disabled');
      $('#annotate_submit_label').removeClass('basic');
    } else{
      $('#annotate_submit_label').removeClass('disabled');
      $('#annotate_submit_label').addClass('basic');
    }
};

function get_pos_color(pos){
  var color_dict = {};

  // SUC tags
  color_dict['AB'] = '#F9EBEA';
  color_dict['DT'] = '#F5EEF8';
  color_dict['HA'] = '#EAF2F8';
  color_dict['HD'] = '#E8F8F5';
  color_dict['HP'] = '#E9F7EF';
  color_dict['HS'] = '#FEF9E7';
  color_dict['IE'] = '#FDF2E9';
  color_dict['IN'] = '#FADBD8';
  color_dict['JJ'] = '#E8DAEF';
  color_dict['KN'] = '#D6EAF8';
  color_dict['NN'] = '#D4EFDF';
  color_dict['MAD'] = '#FDEBD0';
  color_dict['MID'] = '#E6B0AA';
  color_dict['PAD'] = '#D7BDE2';
  color_dict['PC'] = '#A9CCE3';
  color_dict['PL'] = '#F4D03F';
  color_dict['PM'] = '#F9E79F';
  color_dict['PN'] = '#F5CBA7';
  color_dict['PP'] = '#F1948A';
  color_dict['PS'] = '#BB8FCE';
  color_dict['RG'] = '#85C1E9';
  color_dict['RO'] = '#ABEBC6';
  color_dict['SN'] = '#FAD7A0';
  color_dict['UO'] = '#F4F6F6';
  color_dict['VB'] = '#3498DB';

  // UD tags
  color_dict['ADJ'] = '#F9EBEA';
  color_dict['ADP'] = '#F5EEF8';
  color_dict['ADV'] = '#EAF2F8';
  color_dict['AUX'] = '#E8F8F5';
  color_dict['CCONJ'] = '#E9F7EF';
  color_dict['DET'] = '#FEF9E7';
  color_dict['INTJ'] = '#FDF2E9';
  color_dict['NOUN'] = '#FADBD8';
  color_dict['NUM'] = '#E8DAEF';
  color_dict['PART'] = '#D6EAF8';
  color_dict['PRON'] = '#D4EFDF';
  color_dict['PROPN'] = '#FDEBD0';
  color_dict['PUNCT'] = '#E6B0AA';
  color_dict['SCONJ'] = '#D7BDE2';
  color_dict['SYM'] = '#A9CCE3';
  color_dict['VERB'] = '#F4D03F';
  color_dict['X'] = '#F9E79F';

  /*
    Additional unused colors
    #EAEDED
    #D6DBDF
    #E5E7E9
    #BFC9CA
    #ABB2B9
  */

  return color_dict[pos];
}

function toggle_visualise_pos(pos){
  if (document.getElementById("pos_" + pos + "_slider").checked === true){
    console.log('true');
    $(".token").each(function() {
        var norm = $(this).data('xpos')
        if (norm === pos){
          color = get_pos_color(pos);
          $(this).css({'background-color': color});
        }
    });
  } else{
    console.log('false');
    $(".token").each(function() {
        var norm = $(this).data('xpos')
        if (norm === pos){
          $(this).css({'background-color': 'white'});
        }
    });
  }
}

function token_search() {
    var search_query = document.getElementById('search_token').value;

    if (document.getElementById("visualise_slider").checked === true){

      $(".norm").each(function() {
          $(this).removeClass('highlighted');
      });

      $(".norm").each(function() {
          var norm = $(this).data('norm');
          if (typeof(norm) === "string") {
            if (norm.toUpperCase() === search_query.toUpperCase()) {
              $(this).addClass('highlighted');
            }
          }

      });

    } else {
      $(".form").each(function() {
          $(this).removeClass('highlighted');
      });

      $(".form").each(function() {
          var form = $(this).data('form');
          if (typeof(form) === "string") {
            if (form.toUpperCase() === search_query.toUpperCase()) {
              $(this).addClass('highlighted');
            }
          }
      });

    }
}

function apply_text_edit(type, text_id, token_id, new_value){
  queryStr = '?type=' + type + '&text_id=' + text_id + '&token_id=' + token_id + '&new_value=' + new_value
  $.get(url_prefix + '/edit_token' + queryStr, function(data) {

  }).fail(function() {
  alert('Javascript error');


  }).done(function() {
    visualise_text(text_id);

  });
}

function apply_synfeats_edit(type, text_id, sentence_id, new_value){
  queryStr = '?type=' + type + '&text_id=' + text_id + '&sentence_id=' + sentence_id + '&new_value=' + new_value
  $.get(url_prefix + '/edit_synfeats' + queryStr, function(data) {

  }).fail(function(){
    alert('Javascript error');

  }).done(function() {
    visualise_text(text_id);

  });
}

function visualise_text(text_id){
  queryStr = '?text_id=' + text_id
  $.get(url_prefix + '/visualise' + queryStr, function(data) {


    var source = $('#visualise_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#visualise_zone').html(rendered);
    toggle_visualise();
    openTab('page_visualise');
    visualise_sentence_features(data.sentences)
  }).fail(function() {
    alert('Javascript error');
  });
}

function visualise_sentence_features(sentences) {
  $('.ui.accordion').accordion({
    onOpening: function() {
      const idx = this.attr('data-index');
      const sentence = sentences[idx];
      render_sentence_features(sentence, idx);
    }
  });
}

function render_sentence_features(sentence, i) {
  if ($(`#displacy_sent_${i}`).children().length >0) {
    return;
  }

  const displacy = new displaCy('', {
    container: `#displacy_sent_${i}`,
  });
  const parse = displacy_json_from_sentence_data(sentence);
  displacy.render(parse);
  const displacyModal = new displaCy('', {
    container: `#displacy_modal_${i} > div`
  });
  displacyModal.render(parse, {
    distance: 100
  });
}

function displacy_json_from_sentence_data(sentence) {
  var words = sentence.tokens.map(function(original_word) {
    return {
      tag: original_word.upos,
      text: original_word.norm,
    };
  });
  var arcs = []
  sentence.tokens.filter(function(original_word) {
    return original_word.head != 0; // 0 or '0'
  }).forEach(function(original_word) {
    // Minus 1 to fix word index from 1 instead of 0
    var token_id = parseInt(original_word.token_id) - 1;
    var head = parseInt(original_word.head) - 1;
    var arc = {
      // spaCy's JSON format requires start to be always smaller then end
      start: head < token_id ? head : token_id,
      end: head < token_id ? token_id : head,
      label: original_word.deprel,
      dir: head < token_id ? 'left' : 'right',
    };
    arcs.push(arc);
  });
  return {
    arcs,
    words,
  };
}

function showDisplacyModal(index) {
  $(`#displacy_modal_${index}`).modal('show');
}

function edit_text(type, text_id){
  var token_id = document.getElementById("edit_token_id").innerHTML;
  if (token_id === ""){
    return;
  }

  var current = document.getElementById("marked_" + type).innerHTML;

  var n = new Noty({
    type: 'alert',
    layout: 'center',
    theme: 'bootstrap-v4',
    text: '<h3>Ändra ' + type + '</h3>\
    <div class="ui form">\
    <input id="token_edit_field" type="text" value=' + current + '></div>',
    buttons: [
    Noty.button('Spara', 'btn btn-success', function () {
        var new_value = document.getElementById('token_edit_field').value;
        if (new_value.length === 0){
            n.close()
        } else {
          apply_text_edit(type, text_id, token_id, new_value);
          n.close();

        }
    }, {id: 'button1', 'data-status': 'ok', class: 'ui fluid centered_button basic button'}),
    ],
    progressBar: false,
    closeWith: ['button', 'btn btn-success'],
    animation: {
      open: 'noty_effects_open',
      close: 'noty_effects_close'
    },
    id: false,
    force: false,
    killer: false,
    queue: 'global',
    container: false,
    modal: true
  }).show()
}

function edit_synfeats(type, text_id){
  var sentence_id = document.getElementById("edit_sentence_id").innerHTML;
  if (sentence_id == ""){
    return;
  }

  var current = document.getElementById("marked_" + type).innerHTML;

  var n = new Noty({
    type: 'alert',
    layout: 'center',
    theme: 'bootstrap-v4',
    text: '<h3>Ändra ' + type + '</h3>\
    <div class="ui form>"\
    <input id="sentence_edit_field" type="text" value=' + current + '></div>',
    button: [
        Noty.button('Spara', 'btn btn-success', function () {
          var new_value = document.getElementById('sentence_edit_field').value;
          if (new_value.length === 0){
            n.close()
          } else {
            apply_synfeats_edit(type, text_id, sentence_id, new_value);
            n.close();
          }
        },{id:'button1', 'data-status': 'ok', class: 'ui fluid centered_button basic button'}),
    ],
    progressBar: false,
    closeWith: ['button', 'btn btn-success'],
    animation: {
      open:'noty_effects_open',
      close: 'noty_effects_close'
    },
    id: false,
    force: false,
    killer: false,
    queue: 'global',
    container: false,
    model: true
  }).show()
}

function highlight_token(token){
  $(".token").each(function() {
      $(this).removeClass('highlighted');
  });

  document.getElementById("edit_token_id").innerHTML = token.getAttribute("data-id");

  $(token).addClass('highlighted');
  document.getElementById("marked_form").innerHTML = token.getAttribute("data-form");
  document.getElementById("marked_norm").innerHTML = token.getAttribute("data-norm");
  document.getElementById("marked_lemma").innerHTML = token.getAttribute("data-lemma");
  document.getElementById("marked_upos").innerHTML = token.getAttribute("data-upos");
  document.getElementById("marked_xpos").innerHTML = token.getAttribute("data-xpos");
  document.getElementById("marked_feats").innerHTML = token.getAttribute("data-feats");
  document.getElementById("marked_ufeats").innerHTML = token.getAttribute("data-ufeats");
  document.getElementById("marked_head").innerHTML = token.getAttribute("data-head");
  document.getElementById("marked_deprel").innerHTML = token.getAttribute("data-deprel");
  document.getElementById("marked_deps").innerHTML = token.getAttribute("data-deps");
  document.getElementById("marked_misc").innerHTML = token.getAttribute("data-misc");
  document.getElementById("marked_dep_length").innerHTML = token.getAttribute("data-dep-length");
  document.getElementById("marked_path").innerHTML = token.getAttribute("data-path");

  $(token).popup({
    on: 'click',
    exclusive: true,
    popup: '#token_detail_info_popup'
  });
  $(token).popup('show');
}



function highlight_normalized(){
  $(".norm").each(function(){
    if ( $(this).attr('data-normalized') == 'true' ) {
      $(this).toggleClass("underlined");
    }
  });
}

function toggle_visualise(){
  if (document.getElementById("visualise_slider").checked === true){

    $(".norm").each(function() {
        $(this).removeClass("token_hidden");
    });

    $(".form:not(.has_norm)").each(function() {
        $(this).addClass("token_hidden");
    });

    $(".form.has_norm").each(function() {
        $(this).addClass("token_strikethru");
    });

  } else {
    $(".norm").each(function() {
        $(this).addClass("token_hidden");
    });

    $(".form").each(function() {
        $(this).removeClass("token_hidden");
    });

    $(".form.has_norm").each(function() {
        $(this).removeClass("token_strikethru");
    });
  }
  token_search();
}

document.getElementById('file_to_annotate').onchange = function () {
  f = this.value.replace(/.*[\/\\]/, '');
  if (f){
    document.getElementById("choose_file_label").innerHTML = f;
    $('#annotate_submit_label').removeClass('disabled');
    $('#annotate_submit_label').addClass('basic');
  } else {
    document.getElementById("choose_file_label").innerHTML = 'choose file';
    $('#annotate_submit_label').addClass('disabled');
    $('#annotate_submit_label').removeClass('basic');
  }
};

document.getElementById('file_to_analyze').onchange = function () {
  f = this.value.replace(/.*[\/\\]/, '');
  if (f){
    document.getElementById("choose_file_label_analyze").innerHTML = f;
    $('#analyze_submit_label').removeClass('disabled');
    $('#analyze_submit_label').addClass('basic');
  } else {
    document.getElementById("choose_file_label_analyze").innerHTML = 'Välj fil';
    $('#analyze_submit_label').addClass('disabled');
    $('#analyze_submit_label').removeClass('basic');
  }
};

function show_error_msg(message){
  new Noty({
    type: 'alert',
    layout: 'center',
    theme: 'bootstrap-v4',
    text: '<h3>Ett fel har uppstått</h3>' + message,
    progressBar: false,
    closeWith: ['button'],
    animation: {
      open: 'noty_effects_open',
      close: 'noty_effects_close'
    },
    id: false,
    force: false,
    killer: false,
    queue: 'global',
    container: false,
    modal: true
  }).show()
}

function filename_popup(file_id, old_filename){
  var n = new Noty({
    type: 'alert',
    layout: 'center',
    theme: 'bootstrap-v4',
    text: '<h3>Byt namn</h3>\
    <div class="ui form">\
    <input id="new_filename_text" type="text" value=' + old_filename + '></div>',
    buttons: [
    Noty.button('Spara', 'btn btn-success', function () {
        var new_name = document.getElementById('new_filename_text').value;
        if (new_name.length === 0){
            n.close()
        } else {
          set_filename(file_id, new_name);
          n.close();
        }
    }, {id: 'button1', 'data-status': 'ok', class: 'ui fluid centered_button basic button'}),
    ],
    progressBar: false,
    closeWith: ['button', 'btn btn-success'],
    animation: {
      open: 'noty_effects_open',
      close: 'noty_effects_close'
    },
    id: false,
    force: false,
    killer: false,
    queue: 'global',
    container: false,
    modal: true
  }).show()
}

function set_filename(file_id, new_filename){

  queryStr = '?new_filename=' + new_filename + '&file_id=' + file_id
  $.get(url_prefix + '/set_filename' + queryStr, function(data) {


    var source = $('#loaded_texts_template').html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    $('#loaded_texts_zone').html(rendered);
    update_sidebar();
    // initialize_semantic();

  }).fail(function() {
    alert('Javascript error');

  });
}

Handlebars.registerHelper('ifEquals', function(arg1, arg2, options) {
    return (arg1 == arg2) ? options.fn(this) : options.inverse(this);
});

Handlebars.registerHelper('ifNotEquals', function(arg1, arg2, options) {
    return (arg1 != arg2) ? options.fn(this) : options.inverse(this);
});

function initialize_semantic(){
    $('.activating.element').popup();
    $('.tabular.menu .item').tab();
    $('.ui.dropdown').dropdown();
    $('.ui.nodropdown').dropdown({
      action: 'nothing'
    });
    $('.ui.modal').modal();
}

function hasClass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}

function fade_down_main(item){
  $('#' + item).transition('fade down');
}

function fade_down(item){
  $('#' + item).transition('fade down');
  var arrow = document.querySelector('#arrow_' + item)
  arrow.classList.toggle('vertically');
  arrow.classList.toggle('flipped');
}

function show_upload_section(){
  console.log('show_upload');
  $('#upload_annotate_main').css('display', 'none');
  $('#paste_section').css('display', 'none');
  $('#file_select_label').css('display', '');
  $('#upload_annotate_section').css('display', 'block');
  document.getElementById("use_paste").checked = false;
}

function show_paste_section(){
  $('#upload_annotate_section').css('display', 'block');
  $('#upload_annotate_main').css('display', 'none');
  $('#paste_section').css('display', '');
  $('#file_select_label').css('display', 'none');
  document.getElementById("use_paste").checked = true;
}

function annotate_back(){
  $('#upload_annotate_section').css('display', 'none');
  $('#upload_annotate_main').css('display', 'block');
  document.getElementById("file_to_annotate").value = "";
  document.getElementById("pasted_text").value = "";
  document.getElementById("choose_file_label").innerHTML = 'Choose file';
  $('#annotate_submit_label').addClass('disabled');
  $('#annotate_submit_label').removeClass('basic');
}

function download_csv(csv, filename) {
    var csvFile;
    var downloadLink;

    // CSV FILE
    csvFile = new Blob([csv], {type: "text/csv"});

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // We have to create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Make sure that the link is not displayed
    downloadLink.style.display = "none";

    // Add the link to your DOM
    document.body.appendChild(downloadLink);

    // Lanzamos
    downloadLink.click();
}

function export_table_to_csv(tables, filename) {
	var csv = [];
  separator = document.querySelector('input[name="freq_radio"]:checked').value;
  console.log(tables);
  for (i=0; i < tables.length; i++){

    var oTable = document.getElementById(tables[i]);

    for (j = 0; j < oTable.rows.length; j++) {
  		var oCells = oTable.rows.item(j).cells;
      var row = [];
      for (k = 0; k < oCells.length; k++){
          row.push(oCells[k].innerText);
			}
      csv.push(row.join("\t").trim());
    }
  }

  new_csv = csv.join("\n").replace(/\s\s+/g, '\t').replace(/\t#/g, '\n\n#').replace(/Antal\tMedelvärde/g, '\tAntal\tMedelvärde');

  if (separator == 'comma') {
    download_csv(new_csv.replace(/([0-9])\.([0-9])/g, '$1,$2'), filename);
  }
  else{
    download_csv(new_csv, filename);
  }


}

document.querySelector("#export_separated").addEventListener("click", function () {

  separator = document.querySelector('input[name="freq_radio"]:checked').value;

  if (separator === 'comma') {
    queryStr = '?delimiter=comma'
  } else {
    queryStr = '?delimiter=period'
  }

  if (document.getElementById('chk_freq_limit').checked) {
    var freqlimit = document.getElementById('freq_limit_n').value;
    queryStr += '&freq_limit=' + freqlimit;
  }

  if (document.getElementById('chk_general_stats').checked) {
    queryStr += '&general=true'
  }
  if (document.getElementById('chk_pos_stats').checked) {
    queryStr += '&pos=true'
  }
  if (document.getElementById('chk_freq_stats').checked) {
    queryStr += '&freq=true'
  }
  if (document.getElementById('chk_readability_stats').checked) {
    queryStr += '&readability=true'
  }
  if (document.getElementById('chk_syntactic_stats').checked) {
    queryStr += '&syntactic=true'
  }
  if (document.getElementById('chk_morph_stats').checked) {
    queryStr += '&morph=true'
  }
  if (document.getElementById('chk_lexical_stats').checked){
    queryStr += '&lexical=true'
  }


  window.location.replace(url_prefix + '/download_all' + queryStr);

});


document.querySelector("#exportbtn").addEventListener("click", function () {
  var tables = [];

  if (document.getElementById('chk_general_stats').checked) {
    tables.push('table_general');
    tables.push('table_lengths');
  }
  if (document.getElementById('chk_pos_stats').checked) {
    tables.push('table_pos');
  }
  if (document.getElementById('chk_freq_stats').checked) {
    tables.push('table_freq');
  }
  if (document.getElementById('chk_readability_stats').checked) {
    tables.push('table_readability');
  }
  if (document.getElementById('chk_syntactic_stats').checked) {
    tables.push('table_syntactic');
  }
  if (document.getElementById('chk_morph_stats').checked) {
    tables.push('table_morph');
  }
  if (document.getElementById('chk_lexical_stats').checked) {
    tables.push('table_lexical');
  }
  if (tables.length > 0){
    export_table_to_csv(tables, "table.csv");
  }

});


$( document ).ready(function() {
  window.url_prefix = document.getElementById("urls").value;
  openTab('page_annotate');
  update_sidebar();
  initialize_semantic();
});
