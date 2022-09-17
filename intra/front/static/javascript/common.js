

function getNow() {
    var now = new Date();
    var year = now.getFullYear();
    var mon = now.getMonth()+1; //１を足すこと
    var day = now.getDate();
    var hour = now.getHours();
    var min = now.getMinutes();
    var sec = now.getSeconds();

    //出力用
    var s = year.toString().padStart(2, "0") + "/" + mon.toString().padStart(2, "0") + "/" + day.toString().padStart(2, "0") + " " + hour.toString().padStart(2, "0") + ":" + min.toString().padStart(2, "0") + ":" + sec.toString().padStart(2, "0"); 
    return s;
}
