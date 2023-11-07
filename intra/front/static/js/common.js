

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

async function request(url, method, data, csrftoken) {

    let param = {
        method: method,   // GET POST PUT DELETEなど
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    };

    if (!(method == 'GET')) {
        param.body = JSON.stringify(data);
    };
    try {
        const response = await fetch(url, param);

        if (!response.ok) {
            alert('リクエストが失敗しました。' + '[ ' + response.status + ']' + '[ ' + response.statusText + ']')
            throw new Error(`HTTP error: ${response.status}`);
        };

        return response.json();

    } catch (error) {
        console.error(`Error: ${error}`);
    }
};

let onoffHandler = function (event) {
    let h = event.target;
    let onText = h.getAttribute('on-text');
    let offText = h.getAttribute('off-text');
    if (h.textContent == onText) {
        h.textContent = offText;
    } else {
        h.textContent = onText;
    };
};

function setMonthSelector(selectElem, saffix=''){

    while (selectElem.firstChild) {
        selectElem.removeChild(selectElem.firstChild);
    };
    for (var i = 0; i < 12; i++){
        var elem = document.createElement("option");
        elem.setAttribute("value", i + 1);
        elem.innerHTML = (i + 1) + saffix;
        selectElem.appendChild(elem)
    };
};
function setDaySelector(selectElem, saffix=''){
    while (selectElem.firstChild) {
        selectElem.removeChild(selectElem.firstChild);
    };
    for (var i = 0; i < 31; i++){
        var elem = document.createElement("option");
        elem.setAttribute("value", i + 1);
        elem.innerHTML = (i + 1) + saffix;
        selectElem.appendChild(elem)
    };
};

function zeroPlace(time, count) {
    str = '';
    for (let i = 0; i < count; i++) {
        str += '0';
    };
    return (str + time).slice(0 - parseInt(count))
};

function defaultStr(str, default_word) {
    if (str == ''){
        return default_word;
    };

    return str ?? default_word;
};

function isStringEmpty(str) {
    if (!(str?.trim())) {
        return true;
    };
};