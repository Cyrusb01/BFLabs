$.getJSON('/data/btc/0', function (data) {
    createLineChartBetter(data);
});


function createLineChartBetter(dataStore) {
    $('#container').highcharts('StockChart', {

        scrollbar: {
            enabled: false
        },

        chart: {
            backgroundColor: null,
            plotBackgroundColor: null,
            style: {
                fontFamily: 'Open Sans'
            },
            zoomType: 'x',

        },

        navigator: {
            enabled: false
        },

        rangeSelector: {
            selected: 3,
            buttons: [{
                type: 'ytd',
                text: 'YTD'
            }, {
                type: 'year',
                count: 1,
                text: '1Y'
            }, {
                type: 'year',
                count: 2,
                text: '2Y'
            }, {
                type: 'all',
                text: 'Reset'
            }]
        },

        credits: {
            enabled: false
        },

        exporting: {
            enabled: false
        },

        title: {
            text: 'BTC Alpha Predator Systematic vs. Market',
            style: {
                fontSize: '18px'
            }
        },

        subtitle: {
            text: 'Click and drag in the plot area to zoom in'
        },

        plotOptions: {
            series: {
                compare: 'percent'
            }
        },

        yAxis: [{
            offset: 70,
            labels: {
                formatter: function () {
                    return (this.value > 0 ? '+' : '') + this.value + '%';
                }
            }
        }],

        xAxis: {
            events: {
                afterSetExtremes: function (event) {
                    updateStats(dataStore['strategy'], dataStore['market'], dataStore['treasury'],
                        event.min, event.max);
                }
            }
        },

        legend: {
            enabled: true,
            backgroundColor: '#fff',
            borderColor: 'fff',
            layout: 'horizontal',
            verticalAlign: 'bottom',
            borderWidth: 1,
            itemDistance: 30,
            shadow: false
        },

        series: [{
                color: '#C7A967',
                shadow: false,
                lineWidth: 3,
                name: 'AP Strategy',
                data: dataStore['strategy'],
                tooltip: {
                    pointFormat: '<span style="color:{series.color}; font-weight:bold">{series.name}:</span> {point.change}%<br/>',
                    valueDecimals: 2
                }
            },
            {
                color: '#777679',
                shadow: false,
                lineWidth: 2,
                name: 'Market Long',
                data: dataStore['market'],
                tooltip: {
                    pointFormat: '<span style="color:{series.color}; font-weight:bold">{series.name}:</span> {point.change}%<br/>',
                    valueDecimals: 2
                }
            }
        ]
    });
    // compute metrics
    updateStats(dataStore['strategy'], dataStore['market'], dataStore['treasury'],
        dataStore['strategy'][0][0], dataStore['strategy'][dataStore['strategy'].length - 1][0]);
}

function updateStats(data1, spxData, treasuryData, minDate, maxDate) {

    var startDate = parseInt(minDate) - parseInt(minDate) % 86400000;
    var endDate = parseInt(maxDate) - parseInt(maxDate) % 86400000;

    var rollingReturn1;
    var rollingReturn2;
    var spxRollingReturn;

    var numPoints;
    numPoints = ((new Date(endDate)) - (new Date(startDate))) / (1000 * 60 * 60 * 24);

    if (numPoints != null) {
        if (numPoints > 3600) {
            rollingReturn1 = calculateRollingData(250, data1);
            spxRollingReturn = calculateRollingData(250, spxData);

            firstSingularCalculation = new SingularCalculation(data1, rollingReturn1, treasuryData, startDate, endDate, 360 / numPoints, 1);
            spxSingularCalculation = new SingularCalculation(spxData, spxRollingReturn, treasuryData, startDate, endDate, 360 / numPoints, 1);

        } else if (numPoints > 1440) {

            rollingReturn1 = calculateRollingData(60, data1);
            spxRollingReturn = calculateRollingData(60, spxData);

            firstSingularCalculation = new SingularCalculation(data1, rollingReturn1, treasuryData, startDate, endDate, 360 / numPoints, 4);
            spxSingularCalculation = new SingularCalculation(spxData, spxRollingReturn, treasuryData, startDate, endDate, 360 / numPoints, 4);
        } else if (numPoints > 300) {

            rollingReturn1 = calculateRollingData(21, data1);
            spxRollingReturn = calculateRollingData(21, spxData);

            firstSingularCalculation = new SingularCalculation(data1, rollingReturn1, treasuryData, startDate, endDate, 360 / numPoints, 12);
            spxSingularCalculation = new SingularCalculation(spxData, spxRollingReturn, treasuryData, startDate, endDate, 360 / numPoints, 12);
        } else if (numPoints > 70) {

            rollingReturn1 = calculateRollingData(5, data1);
            spxRollingReturn = calculateRollingData(5, spxData);


            firstSingularCalculation = new SingularCalculation(data1, rollingReturn1, treasuryData, startDate, endDate, 360 / numPoints, 52);
            spxSingularCalculation = new SingularCalculation(spxData, spxRollingReturn, treasuryData, startDate, endDate, 360 / numPoints, 52);
        } else {

            rollingReturn1 = calculateRollingData(1, data1);
            spxRollingReturn = calculateRollingData(1, spxData);

            firstSingularCalculation = new SingularCalculation(data1, rollingReturn1, treasuryData, startDate, endDate, 360 / numPoints, 360);
            spxSingularCalculation = new SingularCalculation(spxData, spxRollingReturn, treasuryData, startDate, endDate, 360 / numPoints, 360);
        }
    }

    var annualReturn1 = firstSingularCalculation.annualizeReturn();
    var spxReturn = spxSingularCalculation.annualizeReturn();

    var risk1 = firstSingularCalculation.annualizeRisk();

    var sharpe1 = firstSingularCalculation.sharpe();

    var sortino1 = firstSingularCalculation.sortino();

    var firstAndSpxRelationship = new RelationshipCalculations(rollingReturn1, spxRollingReturn, treasuryData, startDate, endDate, annualReturn1, spxReturn);

    var correlationBetweenFirstTwoSeries = firstAndSpxRelationship.correlation();

    var betaBetweenFirstTwoSeries = firstAndSpxRelationship.beta();

    var alphaBetweenFirstTwoSeries = firstAndSpxRelationship.alpha();

    correlationBetweenFirstTwoSeries = checkIfValid(correlationBetweenFirstTwoSeries);

    betaBetweenFirstTwoSeries = checkIfValid(betaBetweenFirstTwoSeries);

    alphaBetweenFirstTwoSeries = checkIfValidPercent(alphaBetweenFirstTwoSeries);

    annualReturn1 = checkIfValidPercent(annualReturn1);

    risk1 = checkIfValidPercent(risk1);

    sharpe1 = checkIfValid(sharpe1);

    sortino1 = checkIfValid(sortino1);


    document.getElementById("annualReturn").innerHTML = annualReturn1;

    document.getElementById("annualRisk").innerHTML = risk1;

    document.getElementById("sharpe").innerHTML = sharpe1;

    document.getElementById("sortino").innerHTML = sortino1;

    document.getElementById("correlation").innerHTML = correlationBetweenFirstTwoSeries;

    document.getElementById("beta").innerHTML = betaBetweenFirstTwoSeries;

    document.getElementById("alpha").innerHTML = alphaBetweenFirstTwoSeries;
}