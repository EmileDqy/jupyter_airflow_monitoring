function checkWidth(text, fontSize, fontFamily) {
    var temp = $('<span>').html(text).css({ 'font-size': fontSize, 'font-family': fontFamily, visibility: 'hidden', whiteSpace: 'nowrap' });
    $('body').append(temp);
    var width = temp.width();
    temp.remove();
    return width;
}

define([
    'base/js/namespace',
    'jquery',
    'base/js/utils'
], function (Jupyter, $, utils) {
    function load_ipython_extension() {
        // Define the URL of your CSS file.
        var cssUrl = utils.get_body_data('baseUrl') + 'nbextensions/jupyter_airflow_monitoring/main.css';

        // Create a new link element.
        var link = document.createElement('link');

        // Set the attributes of the link element.
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = cssUrl;

        // Append the link element to the head of the document.
        document.getElementsByTagName('head')[0].appendChild(link);

        // Initialize button and modal
        var button = $('<button id="header-message" class="btn btn-primary button"></button>')
            .addClass("button")
            .attr("data-title", "Airflow");


        var modal = $(
            '<div class="modal fade" tabindex="-1" role="dialog">' +
            '  <div class="modal-dialog" role="document">' +
            '    <div class="modal-content">' +
            '      <div class="modal-header">' +
            '        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
            '        <h3 class="modal-title">Airflow Monitoring Dashboard</h3>' +
            '      </div>' +
            '      <div class="modal-body">' +
            '      </div>' +
            '      <div class="modal-footer">' +
            '        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '</div>'
        );

        button.on('click', function () {
            modal.modal('show');
        });

        $('#header-container > :nth-last-child(2)').before(button);
        $('body').append(modal);

        var last_response = undefined;

        var getMessage = function () {
            $.ajax({
                url: utils.get_body_data('baseUrl') + 'message',
                success: function (response) {
                    var message = response.message;
                    var title = response.title;
                    var color = response.color;
                    
                    if ( JSON.stringify(last_response) !== JSON.stringify(response)) {
                        last_response = response
                        if (!message || !title) {
                            button.hide();
                            return;  // Don't show the button if message or title are missing
                        }else{
                            button.show();
                        }
    
                        var padding = 10;
                        
                        var textWidthAirflow = checkWidth('Airflow', $('.button').css('font-size'), $('.button').css('font-family'));
                        var textWidthTitle = checkWidth(title, $('.button').css('font-size'), $('.button').css('font-family'));
                        var maxWidth = 20 * 16;
                        
                        var shouldScroll = false;
                        if (textWidthTitle > maxWidth) {
                            textWidthTitle = maxWidth;
                            shouldScroll = true;
                            console.log("Should scroll by itself");
                        }
                        
                        button.css('background-color', color);
                        button.css('width', (textWidthAirflow + padding) + 'px');
    
                        button.hover(
                            function () {
                                console.log('Hover in');
                                $(this).addClass('hovered');
                                $(this).attr("data-title", title);
                                $(this).css('width', (textWidthTitle + padding) + 'px');
                                if (shouldScroll) {
                                    $(this).addClass("scrollable");
                                }
                            },
                            function () {
                                console.log('Hover out');
                                $(this).removeClass('hovered');
                                $(this).attr("data-title", "Airflow");
                                $(this).css('width', (textWidthAirflow + padding) + 'px');
                                if (shouldScroll) {
                                    $(this).removeClass("scrollable");
                                }
                            }
                        );                    
    
                        // Update modal content
                        modal.find('.modal-body').html(message);

                    }

                }
            });
        };

        getMessage();
        setInterval(getMessage, 10000);
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});