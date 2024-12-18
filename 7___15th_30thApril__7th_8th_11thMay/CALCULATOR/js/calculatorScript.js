// alert('fahimah')
const getInput = inputId => parseInt(document.getElementById(inputId).value) ;


const showResult = result=> document.getElementById('result').innerHTML = result;


// function add(){
//     const input1 = getInput('input1');
//     const input2 = getInput('input2');
//     const addedRes = input1+input2;
//     showResult(addedRes)
// }

// function subtract(){
//     const input1 = getInput('input1');
//     const input2 = getInput('input2');
//     const addedRes = input1-input2;
//     showResult(addedRes)
// }
function arithaaticOperation(operation){
    
    const input1 = getInput('input1');
    const input2 = getInput('input2');
    let result;
    if(operation === '+'){
        result = input1 + input2;
    }
    else if(operation === '-'){
        result = input1 - input2;
    }
    return result;
}

function add(){
    showResult(arithaaticOperation('+'));
}

function subtract(){
    showResult(arithaaticOperation('-'));
}