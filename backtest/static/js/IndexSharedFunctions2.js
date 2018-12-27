
function checkIfValid(value){
	return (isNaN(parseInt(value)) ? 'N/A':parseFloat(parseInt(value *100)/100).toFixed(2));
}

function checkIfValidPercent(value){
	return (isNaN(parseInt(value)) ? 'N/A':parseFloat(parseInt(value *10000)/100).toFixed(2) +'%'); 

}

function calculateBeginning(startPoint, leadPoints){
	while(leadPoints[startPoint] != null){
		startPoint++;
	}
	return startPoint;
}


function searchForDateIndex(date, array){
	//console.log(date);
	//console.log(array);
	for(var i = 0;i<array.length;i++){
		
		if(array[i][0] >= date){
			
			return i;
		}
	}
	return 0;
}
function findShortestArray(array1, array2){
	tmp = []
	j=0;
	  if(array1.length > array2.length) {
		startPoint = array1.length- array2.length;
	for(var i = startPoint; i < array1.length;i++){
		tmp[j++] = array1[i];
	}
	} else {
		startPoint = array2.length- array1.length;
		for(var i = startPoint; i < array2.length;i++){
		tmp[j++] = array2[i];
	}
	}
	return tmp;
}

function calculateStandardDeviation(arrayOfValues){

	return Math.sqrt(calculateVariance(arrayOfValues));
}
function calculateCovariance(array1, array2){
	var shortArray = findShortestArray(array1,array2);
	if(array1.length > array2.length) {
		array1 = shortArray;
	}
	else{
		array2 = shortArray;
	}
	var mean1 = 0;
	var mean2 = 0;
	var size = array1.length > array2.length ? array2.length : array1.length;
	for(var i = 0;i<size;i++){
		mean1 += array1[i];
		mean2 += array2[i];
	}
	mean1 /= size;
	mean2 /=size;

	var covariance = 0;
	//assume array is same size
	for(var i = 0;i<size;i++){
		covariance += (array1[i]-mean1) * (array2[i]-mean2);
	}

	return covariance/size;

}

function calculateVariance(array1){

	var mean = 0;
	for(var i = 0;i<array1.length;i++){
		mean += array1[i];
	}
	mean /= array1.length;

	var variance = 0;
	for(var i = 0;i<array1.length;i++){
		variance += Math.pow(array1[i]-mean, 2);
	}
	return variance/(array1.length);
}


function getPearsonCorrelation(x, y) {
	var shortestArrayLength = 0;
	var shortArray = findShortestArray(x,y);

	if(x.length == y.length) {
		shortestArrayLength = x.length;
	} else if(x.length > y.length) { // x has more elements create tmp array, starting at index startPoint
		shortestArrayLength = y.length;
	x= shortArray;
	} else { // y has more elements create tmp array, starting at index startPoint
		shortestArrayLength = x.length;
	y = shortArray;
	}
	var xy = [];
	var x2 = [];
	var y2 = [];


	for(var i=0; i<shortestArrayLength; i++) {
		xy.push(x[i] * y[i]);
	
		x2.push(x[i] * x[i]);

		y2.push(y[i] * y[i]);
		
	}



	var sum_x = 0;
	var sum_y = 0;
	var sum_xy = 0;
	var sum_x2 = 0;
	var sum_y2 = 0;


	for(var i=0; i< shortestArrayLength; i++) {
		sum_x += parseFloat(x[i])	
		sum_y += parseFloat(y[i]);
		sum_xy += parseFloat(xy[i]);
		sum_x2 += parseFloat(x2[i]);
		sum_y2 += parseFloat(y2[i]);
	}
	


	var step1 = (shortestArrayLength * sum_xy) - (sum_x * sum_y);
	
	var step2 = (shortestArrayLength * sum_x2) - (sum_x * sum_x);
	
	var step3 = (shortestArrayLength * sum_y2) - (sum_y * sum_y);
	
	var step4 = Math.sqrt(step2 * step3);
	
	var answer = step1 / step4;

	return answer;
}

function calculateRollingData(rollingPeriod, data){
	var arrayToReturn = [];
	for(var i = rollingPeriod;i<data.length;i++){
		arrayToReturn.push([data[i][0],data[i][1]/data[i-rollingPeriod][1]-1]);

	}
	return arrayToReturn;
}


function SingularCalculation(data, rollingReturn, treasuryYield, minDate, maxDate, adjustment1, adjustment2){
	this.data = data;
	this.rollingReturn = rollingReturn;
	this.treasuryYield = treasuryYield; 
	this.minDate = minDate;
	this.maxDate = maxDate;
	this.adjustment1 = adjustment1;
	this.adjustment2 = adjustment2;
}

SingularCalculation.prototype.annualizeReturn = function(){

	if(this.data == null){
		return 'N/A';
	}
	var startIndex = searchForDateIndex(this.minDate, this.data);
	var endIndex = searchForDateIndex(this.maxDate, this.data);
	var annReturn =  Math.pow(this.data[endIndex][1]/this.data[startIndex][1],this.adjustment1)-1;
	return annReturn;

}

SingularCalculation.prototype.annualizeRisk = function(){

	var annualReturn = this.annualizeReturn();
	if(isNaN(parseFloat(annualReturn))){
		return 'N/A';
	}

	var startIndex = searchForDateIndex(this.minDate, this.rollingReturn);
	var endIndex = searchForDateIndex(this.maxDate, this.rollingReturn);


	if(startIndex == undefined){
		startIndex = 0;
	}


	var tempArray = [];


	for(var i = startIndex;i<=endIndex;i++){
		if(this.rollingReturn[i][1] != null && !isNaN(parseFloat(this.rollingReturn[i][1])) && parseFloat(this.rollingReturn[i][1]) != Infinity){
			tempArray.push(parseFloat(this.rollingReturn[i][1]));
		}
	}

	var stdDev = calculateStandardDeviation(tempArray) * Math.sqrt(this.adjustment2);
	return stdDev;
}

SingularCalculation.prototype.sharpe = function(){

	var annualReturn = this.annualizeReturn();
	var annualRisk = this.annualizeRisk();
	


	if(annualRisk == null || annualReturn == null){
		return 'N/A';
	}

	var startIndex = searchForDateIndex(this.minDate, this.treasuryYield);
	var endIndex = searchForDateIndex(this.maxDate, this.treasuryYield);
	var mean = 0;
	for(var i = startIndex;i<=endIndex;i++){
		if(!isNaN(parseFloat(this.treasuryYield[i][1]))){
					mean += parseFloat(this.treasuryYield[i][1]);
			}
		
	}

	mean/=(endIndex-startIndex);
	return (annualReturn-mean) / annualRisk;
}
SingularCalculation.prototype.sortino =  function(){

	var annualReturn = this.annualizeReturn();
	
	var startIndex = searchForDateIndex(this.minDate, this.rollingReturn);
	var endIndex = searchForDateIndex(this.maxDate, this.rollingReturn);
	
	

	if(startIndex == undefined){
		
		startIndex = 0;
	}



	var mean = 0;
	var sum = 0;
	var count = 0;

	for(var i = startIndex;i<=endIndex;i++){
		if(!isNaN(parseFloat(this.rollingReturn[i][1]))){
			
		
			if(!isNaN(parseFloat(this.treasuryYield[i][1]))){
					mean += this.treasuryYield[i][1];
			}
			
			
			if(this.rollingReturn[i][1] < 0){
				sum += Math.pow(this.rollingReturn[i][1], 2);
			}
			count++;
		}

	}
	
	mean/=(count);
	
	var bottom = Math.sqrt(sum/(count));
	
	var returnedValue = (annualReturn - mean) / bottom;
	
	return returnedValue;
}


function RelationshipCalculations(rollingReturn1,rollingReturn2, treasuryYield, minDate, maxDate, annualReturn1, annualReturn2){
	this.rollingReturn1 = rollingReturn1;
	this.rollingReturn2 = rollingReturn2;
	this.treasuryYield = treasuryYield;
	this.minDate = minDate;
	this.maxDate = maxDate;
	this.annualReturn1 = annualReturn1;
	this.annualReturn2 = annualReturn2;
}


RelationshipCalculations.prototype.correlation = function(){

	if(this.rollingReturn1 == null || this.rollingReturn2 == null || isNaN(parseFloat(this.annualReturn1)) || isNaN(parseFloat(this.annualReturn2))){
		return 'N/A';
	}
	


	var startIndex2 = searchForDateIndex(this.minDate, this.rollingReturn2);

	var startIndex1 = searchForDateIndex(this.minDate, this.rollingReturn1);
	var endIndex = searchForDateIndex(this.maxDate, this.rollingReturn1);
	var startIndex = startIndex1 > startIndex2 ? startIndex1 : startIndex2;

	if(startIndex == undefined){
		startIndex = 0;
	}

	var tempArray1 = [];
	var tempArray2 = [];

	for(var i = startIndex;i<endIndex;i++){
		if(this.rollingReturn1[i][1] != null && !isNaN(parseFloat(this.rollingReturn1[i][1]))){
			if(parseFloat(this.rollingReturn1[i][1]) != Infinity){
				tempArray1.push(parseFloat(this.rollingReturn1[i][1]));
			}
			if(parseFloat(this.rollingReturn2[i][1]) != Infinity && !isNaN(parseFloat(this.rollingReturn2[i][1]))){
				tempArray2.push(parseFloat(this.rollingReturn2[i][1]));
			}
		}
	}


	return getPearsonCorrelation(tempArray1, tempArray2);
}

RelationshipCalculations.prototype.beta =  function(){
	if(this.rollingReturn1 == null || this.rollingReturn2 == null || isNaN(parseFloat(this.annualReturn1)) || isNaN(parseFloat(this.annualReturn2))){
		return 'N/A';
	}
	var startIndex1 = searchForDateIndex(this.minDate, this.rollingReturn1);
	var startIndex2 = searchForDateIndex(this.minDate, this.rollingReturn2);

	var startIndex = startIndex1 > startIndex2 ? startIndex1 : startIndex2;
	
	var endIndex = searchForDateIndex(this.maxDate, this.rollingReturn1);

	if(startIndex == undefined){
		startIndex = 0;
	}

	var tempArray1 = [];
	var tempArray2 = [];

	
	for(var i = startIndex;i<=endIndex;i++){
		if(this.rollingReturn1[i][1] != null && !isNaN(parseFloat(this.rollingReturn1[i][1])) && this.rollingReturn1[i][1] != Infinity){
			tempArray1.push(parseFloat(this.rollingReturn1[i][1]));	
		}
		if(this.rollingReturn2[i][1] != null && !isNaN(parseFloat(this.rollingReturn2[i][1])) && this.rollingReturn2[i][1] != Infinity){
			tempArray2.push(parseFloat(this.rollingReturn2[i][1]));
		}

	}
	var covariance = calculateCovariance(tempArray1, tempArray2);
	var variance = calculateVariance(tempArray2);

	return covariance/variance;
}

RelationshipCalculations.prototype.alpha =  function(){
	var beta = this.beta();
	if(this.annualReturn1 == null || this.annualReturn2 == null){
		return 'N/A';
	}

	var startIndex1 = searchForDateIndex(this.minDate, this.rollingReturn1);
	var startIndex2 = searchForDateIndex(this.minDate, this.rollingReturn2);

	var startIndex = startIndex1 > startIndex2 ? startIndex1 : startIndex2;
	var endIndex = searchForDateIndex(this.maxDate, this.treasuryYield);

	if(startIndex == undefined){
		startIndex = 0;
	}
	//startIndex = calculateBeginning(startIndex, this.treasuryYield);

	var treasuryMean = 0;
	var spxMean = 0;

	var count = 0;

	for(var i = startIndex;i<=endIndex;i++){
		if(this.treasuryYield[i][1] != null && !isNaN(parseFloat(this.treasuryYield[i][1]))){
			treasuryMean+=parseFloat(this.treasuryYield[i][1]);
			count++;
		}
	}


	treasuryMean/=count;


	return this.annualReturn1 - treasuryMean - beta * (this.annualReturn2 - treasuryMean);
}
