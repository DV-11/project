$("img").slice(17,).hide()
$("div.tekst").slice(16,).hide()
$("aside").slice(16,).hide()
var m = 17
var n = 16

function Showmore() {
    m += 16;
    n += 16;
    $("img").slice(17,m).show();
    $("div.tekst").slice(16,n).show();
    $("aside").slice(16,n).show();
    if (m > 64) {
        $("div.button").hide();
    }
}
