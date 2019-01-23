 document.getElementById("scroll-content").addEventListener("scroll", function (event) {
     var newDiv = document.createElement("div");
        newDiv.innerHTML = "my awesome new div";
        document.getElementById("scroll-content").appendChild(newDiv);
});


var checkForNewDiv = function () {
    var lastDiv = document.querySelector("#scroll-content > div:last-child");
    var maindiv = document.querySelector("#scroll-content");
    var lastDivOffset = lastDiv.offsetTop + lastDiv.clientHeight;
    var pageOffset = maindiv.offsetTop + maindiv.clientHeight;
    if (pageOffset > lastDivOffset - 10) {
        var newDiv = document.createElement("div");
        newDiv.innerHTML = "my awesome new div";
        document.getElementById("scroll-content").appendChild(newDiv);
        checkForNewDiv();
    }
};

checkForNewDiv();