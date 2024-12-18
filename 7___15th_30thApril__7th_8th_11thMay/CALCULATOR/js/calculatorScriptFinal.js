// alert('fahimah')
const getInput = inputId => parseInt(document.getElementById(inputId).value) ;


const showResultForSum = result=> document.getElementById('result').innerHTML = `sum = ${result}`;
const showResultForSub = result=> document.getElementById('result').innerHTML = `sub = ${result}`;


function arithmaticOperation(operation, showResultCallbackFunction){
    
    const input1 = getInput('input1');
    const input2 = getInput('input2');
    let result;
    if(operation === 'doAdd'){
        result = input1 + input2;
    }
    else if(operation === 'doSub'){
        result = input1 - input2;
    }
    showResultCallbackFunction(result);
}

function add(){
    arithmaticOperation('doAdd', showResultForSum)
}

function subtract(){
    arithmaticOperation('doSub', showResultForSub)
}