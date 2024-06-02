const MODE = {
    AUTOMATIC: 0,
    MANUAL: 1
}

const COLOR_1 = "#B8D8D8"
const COLOR_2 = "#7A9E9F"
const COLOR_3 = "#4F6367"
const COLOR_4 = "#EEF5DB"
const COLOR_5 = "#FE5F55"

const ACTIVE_MODE_COLOR = "#B8D8D8"
const DEACTIVE_MODE_COLOR = "#7A9E9F"

var actual_mode = MODE.MANUAL

document.addEventListener('DOMContentLoaded', function() {
    reset()
})

function reset(){
    document.getElementById("scenarioImage").src = "./Images/DEFAULT_GUI.svg"
    active_button("DEFAULT_BUTTON")
}

function enable_auto(){
    document.getElementById("option-button-0").style.backgroundColor = ACTIVE_MODE_COLOR;
    document.getElementById("option-button-1").style.backgroundColor = DEACTIVE_MODE_COLOR;
    actual_mode = MODE.AUTOMATIC
    document.getElementById("mode-container-automatic").style.display = 'flex';
    document.getElementById("mode-container-manual").style.display = 'none';
    //Disabilita scritta manual
    //Attiva scritta auto
    //Disabilita la visione del div manual
    //Abilita la visione del div automatic
}

function enable_manual(){
    document.getElementById("option-button-0").style.backgroundColor = DEACTIVE_MODE_COLOR;
    document.getElementById("option-button-1").style.backgroundColor = ACTIVE_MODE_COLOR;
    actual_mode = MODE.MANUAL
    document.getElementById("mode-container-automatic").style.display = 'none';
    document.getElementById("mode-container-manual").style.display = 'flex';
    //Disabilita scritta automatic
    //Abilita scritta manual
    //Disabilita la visione del div auto
    //Abilita la visione del div manual
}
