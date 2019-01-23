
var wrapper = document.getElementById("wrapper");

wrapper.addEventListener("scroll", function (event) {
    checkForNewDiv();
});

var checkForNewDiv = function () {
    var lastDiv = document.querySelector("#scroll-content > div:last-child");
    var lastDivOffset = lastDiv.offsetTop + lastDiv.clientHeight;
    var pageOffset = wrapper.scrollTop + wrapper.clientHeight;

    if (pageOffset > lastDivOffset - 10) {
        var newDiv = document.createElement("div");
        newDiv.innerHTML = "my awesome new div";
        document.getElementById("scroll-content").appendChild(newDiv);
        checkForNewDiv();
    }
};

checkForNewDiv();

$("img").slice(20).hide()