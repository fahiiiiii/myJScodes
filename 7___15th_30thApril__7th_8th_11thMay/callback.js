function showText(text) {
    console.log(text);
}
showText("I am Fahimah");
let a = 10;
(function () {
    let a = 20;
    return function () {
        console.log(a);
    };
})()();

// ------------------------------------------------------------------

function doStep1(value) {
    return value + 1;
}
function doStep2(value) {
    return value + 2;
}
function doStep3(value) {
    return value + 3;
}
function doStep() {
    let result = 0;
    result = doStep1(result);
    result = doStep2(result);
    result = doStep3(result);
    console.log(result)
}

doStep();

// _________________________________________________________________

function dS1(value, callback) {
    const result = value + 1;
    callback(result);
}
function dS2(value, callback) {
    const result = value + 2;
    callback(result);
}
function dS3(value, callback) {
    const result = value + 3;
    callback(result);
}
function ds() {
    let answer = 0;
    dS1(answer, function (answer) {
        dS2(answer, function (answer) {
            dS3(answer, function (answer) {
                console.log(answer);
            })
        })
    })
}
ds()


// __________________________________________________________________


function haveText(text, callback) {
    const name = text;
    callback(name)
}
function showText(text) {
    console.log(text);
}
let text = "Fahimah is my name..!"
haveText(text, function (textt) {
    showText(textt)
})






