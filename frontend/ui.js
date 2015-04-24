function populateSelect(maxRoundNum) {
    var selectElem = document.getElementById('roundNum');
    for (var i = 1; i <= maxRoundNum; i++) {
        var optionElem = document.createElement('option');
        optionElem.innerHTML = i;
        selectElem.appendChild(optionElem);
    }
    selectElem.selectedIndex = 0; // Not working!?
}

// https://jqueryui.com/slider/#hotelrooms
function setupSlider(maxRoundNum) {
    var select = $( "#roundNum" );
    var slider = $( "<div id='slider' style='float: right; width: 80%'></div>" ).insertAfter( select ).slider({
      min: 1,
      max: maxRoundNum,
      range: "min",
      value: select[ 0 ].selectedIndex + 1,
      slide: function( event, ui ) {
        select[ 0 ].selectedIndex = ui.value - 1;
        plotRound(data, ui.value);
      }
    });
    $( "#roundNum" ).change(function() {
      slider.slider( "value", this.selectedIndex + 1 );
      plotRound(data, this.selectedIndex + 1);
    });
}

function plotRound(data, roundNum) {
    var options = {
        series: {
            lines: { show: false },
            points: { show: true, fill: true, fillColor: false },
            shadowSize: 0
        },
        // http://colorbrewer2.org/
        colors: ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"]
    };
    $.plot("#placeholder", data[roundNum - 1], options);
}
