
/**
* Description:
*
*/
function showPythonBlog() {
    $.ajax({
       url: "/python_blog",
       type: "get",
       data: {},
       success: function(response){
           $('#page_content').html(response)
       }
    });
};

/**
* Description:
*
*/
function showArticlesForBlog(blogType, articleName) {
    $.ajax({
        url: "/fetch_blog_article/" + blogType + "::" + articleName,
       type: "get",
       data: {},
       success: function(response){
           $('#blog_content').html(response)
       }
    });
    window.scrollTo(0, 0);
};

/**
* Description:
*
*/
function showMainPage() {
    $.ajax({
       url: "/show_main_page",
       type: "get",
       data: {},
       success: function(response){
           $('#page_content').html(response)
       }
    });
};


/**
* Description: Get HTML content for rightpane/content
*
* :param: sGetContent: page to be fetched
*/
function switchMenu(sGetContent) {
    $.ajax({
       url: "/get_page_content/"+sGetContent,
       type: "get",
       data: {},
       success: function(response){
           $('#page_content').html(response)
       }
    });
};

/**
* Description: Get HTML content for rightpane/content
*
* :param: sGetContent: page to be fetched
*/
function getQuotes() {
    $.ajax({
       url: "/get_quotes",
       type: "get",
       data: {},
       success: function(response){
           $('#page_content').html(response)
       }
    });
};
