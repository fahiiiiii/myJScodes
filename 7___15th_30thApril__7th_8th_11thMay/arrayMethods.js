const names = ['Faruk','Shilpe' ,'Mahera','Salif','Mahin','Fahimah'];
const nameStr = names.join(" *-* ")
console.log(names)
console.log(nameStr)

//Array er last e element add kora jay push() function diye 
names.push("FahiMahin");
console.log(names);

//Array er last er element delete kora jay pop() function diye 
names.pop();
console.log(names);

//Array er first er element delete kora jay shift() function diye ,so index ek ghor shift hoy bame
names.shift();
console.log(names);

//Array er first e element add kora jay unshift() function diye 
names.unshift("Faruk")
console.log(names)

//Array er jekono element er value change
names[5]="Fahiiiiiiiimah"
console.log(names)

const arrayOfNumber = [1,2,3,4,6,5,9,7,8,0];
arrayOfNumber.splice(2,4)
console.log(arrayOfNumber)

const arrayConcate = names.concat(arrayOfNumber);
console.log(arrayConcate);

const arrayfrom1to10 = [1,2,3,4,5,6,7,8,9,10];
const oddNumbers = arrayfrom1to10.filter(function(number){
    return ((number % 2) !== 0);
});
console.log(oddNumbers);

//Use of filter() function
const marks = [56,78,89,17,45,23,67,66]
const passedMarks = marks.filter(function(mark){
    return (mark >= 50) 
})
console.log(passedMarks)

//Use of map() function
// const marks = [56,78,89,17,45,23,67,66]
const marksDouble = marks.map(function(mark){
    return mark*2;
})
console.log(marksDouble);

const marksDouble_withoutChangingSecondIndex = marks.map(function(mark,index){
    if(index===2){
        return mark;
    }
    return mark*2;
})
console.log(marksDouble_withoutChangingSecondIndex);

//Use of every() function
const allPassed = marks.every(function(mark){
    return mark >= 50;
})
console.log(allPassed)

const prices = [57,108,19,22,7,9,78];
const overPrice = prices.every(function(price){
    return price >10 ;
})
const underPrice = prices.every(function(price){
    return price <= 10;
})
console.log(overPrice);
console.log(underPrice);

const marksForHighestSearch =[68,70,66,88,99,81,77];
const marksGetAtleastA_minus = marksForHighestSearch.every(function(mark){
    return mark>60
})
console.log(marksGetAtleastA_minus)

//Use of some() function
const atLeastOneA_plus = marks.some(function(mark){
    return mark >= 80;
})
console.log(atLeastOneA_plus);

//add items by Splice() function
// const names = ['Faruk','Shilpe' ,'Mahera','Salif','Mahin','Fahimah'];
names.splice(2,0,"FahiMahin");
console.log(names)

const arrayAlph = ['a','b',1,4,'c','7'];
arrayAlph.splice(4,0,'d','e','f')
console.log(arrayAlph)

//add items by Splice() function
const arrNum = [1,2,3,'c',4,5,6]
arrNum.splice(3,1);
console.log(arrNum)

//slice an array by Slice() function
console.log(arrNum.slice(1,4));
console.log(arrNum.slice(1));

//Array sorting by sort function
const nums = [3,4,12,67,3,7,79];
nums.sort(function(a,b){
  
    return 0;
    
})
console.log(nums);
nums.sort(function(a,b){
    if(a<b){return -1;}
    return 1;
    
})
console.log(nums);
// or 
nums.sort(function(a,b){
    return a-b;
})
console.log(nums);
nums.sort(function(a,b){
    if(a>b){return -1;}
    return 1;
    
})
console.log(nums);
nums.sort(function(a,b){
    return b-a;
})
console.log(nums);

//Array er kono element er index ber korte findIndex()
// const nums = [3,4,12,67,3,7,79];
console.log(nums.findIndex(function(item){
    return item === 12;
}))

//kono specific condition er under e  kongullaa  mmeeet kkorree sshhegulla ooutput dey
console.log(nums.find(function(item){
    return ((item%3) === 0);
}))