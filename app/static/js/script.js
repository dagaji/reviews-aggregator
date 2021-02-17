var page_num = 0;

(function (global) {

var controller = {};

const ajax_url = new URL(request_url, document.location);
const ajax_params = new URLSearchParams(request_params);

// Convenience function for inserting innerHTML for 'select'
function insert_new_content(main_div, responseText) {
  var new_div = document.createElement('div');
  new_div.setAttribute('page-num', page_num);
  new_div.innerHTML = responseText;
  main_div.appendChild(new_div);

  var next_page_button = main_div.querySelector("#next_page");
  if (next_page_button){
    next_page_button.addEventListener("click", next_page, false);
  }
};


// On page load (before images or CSS)
document.addEventListener("DOMContentLoaded", function (event) {

  $(".checkbox-menu").on( 'change', "input[type='radio']", function() {
    $(this).parents('.dropdown-menu').find('li').removeClass('active');
    $(this).parents('.dropdown-menu').find("input[type='radio']").prop('checked', false);
    $(this).closest("li").addClass('active');
    $(this).prop('checked', true);
  });
  
  $(".checkbox-menu").on("change", "input[type='checkbox']", function () {
    $(this).closest("li").toggleClass("active", this.checked);
  });
  
  $(document).on('click', '.allow-focus', function (e) {
    e.stopPropagation();
  });
  
  ["reviewer", "posted_date", "order"].forEach(name => $(`.dropdown button[name="${name}"] ~ ul input`).first().trigger("click"));
  
  function set_filter_params(name, options){
    options.forEach(opt => $(`.dropdown button[name="${name}"] ~ ul input[name="${opt}"]`).trigger("click"));
  }
  Object.keys(request_params).forEach(key => set_filter_params(key, request_params[key].split(',')));

  ajax_url.search = ajax_params
  $ajaxUtils.sendGetRequest(
    ajax_url.toString(),
    function (responseText) {
      var main_div = document.querySelector("#main-content");
      insert_new_content(main_div, responseText);

      document.querySelector("#filter-btn")
        .addEventListener("click", filter_reviews, false);

      document.querySelector(".navbar-collapse form").setAttribute('onsubmit', "return false;")
      document.querySelector("#search-filter-btn")
        .addEventListener("click", search_filter, false);

    },
    false);
});


function search_filter(){
  var search_text = document.querySelector("#search-filter-text").value;
  if (search_text !== ""){
    var reload_url = new URL(window.location);
    reload_url.search = new URLSearchParams({search: search_text});
    window.location.assign(reload_url.toString());
  }
}


function filter_reviews(){
  filters = {};
  var set_filters = function(dropdown_anchor){
    filter_name = dropdown_anchor.querySelector("button").name;
    filters[filter_name] = new Array();
    Array.from(dropdown_anchor.querySelectorAll("li[class='active'] > label > input"))
    .forEach(input_el => filters[filter_name].push(input_el.name));
    if (!filters[filter_name].length){
      delete filters[filter_name];
    }
  };
  Array.from(document.querySelectorAll(".dropdown")).forEach(div => set_filters(div));
  var reload_url = new URL(window.location);
  reload_url.search = new URLSearchParams(filters);
  window.location.assign(reload_url.toString());
}

// Load the menu categories view
function next_page() {
  page_num += 1;
  ajax_params.set("page_num", page_num);
  ajax_url.search = ajax_params;
  console.log(ajax_url.toString());
  // showLoading("#main-content");
  $ajaxUtils.sendGetRequest(
    ajax_url.toString(),
    function (responseText) {
      var main_div = document.querySelector("#main-content");
      main_div.querySelector("#next_page").remove();
      insert_new_content(main_div, responseText);
    },
    false);
};

})(window);
