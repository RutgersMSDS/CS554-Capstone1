document.oncontextmenu = rightClick;
var currentGSE = ''

function openNotes(evt, notetype) {
    var i, tablinks;
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    evt.currentTarget.className += " active";
    PublicNotes = document.getElementById('Public');
    PrivateNotes = document.getElementById('Private');
    if (notetype == "Public") {
        PublicNotes.style.display = "block";
        PrivateNotes.style.display = "none";
    } else {
        PublicNotes.style.display = "none";
        PrivateNotes.style.display = "block";
    }
}

function SelectAll() {
    var checkboxes = document.getElementsByClassName('checkitem');
    for (box of checkboxes) {
        if (box.checked) {
            box.checked = "False"
        } else {
            box.checked = "True"
        }

    }
}

function LoadData() {
    // var data = $('GSEData');
    $.ajax({
        url: '/GetGSEData',
        data: {
            'type': 'render'
        },
        dataType: 'json',
        success: function (response) {
            var arrHead = new Array();
            arrHead = ['GSE', 'Year', 'Subject', 'Organ', 'Source', 'Samples', 'Assay', 'Platform', 'Title'];
            var empTable = document.createElement('table');
            empTable.setAttribute('id', 'GSEData');  // table id.
            empTable.setAttribute('class', 'table table-bordered table-hover table-sm w-75');


            var tr = empTable.insertRow(-1);

            for (var h = 0; h < arrHead.length; h++) {
                var th = document.createElement('th')
                th.setAttribute('class', 'w-auto'); // the header object.
                th.innerHTML = arrHead[h];
                tr.appendChild(th);
            }

            var div = document.getElementById('loadeddata');
            div.appendChild(empTable);    // add table to a container.

            var rowCnt = empTable.rows.length;    // get the number of rows.

            for (var i = 0; i < response.length; i++) {
                row = response[i]
                var tr = empTable.insertRow(rowCnt); // table row.
                tr.setAttribute('id', row[arrHead[0]])
                // tr.addEventdictener(oncontextmenu,rightClick($('tr')))

                for (var c = 0; c < Object.keys(row).length; c++) {
                    var td = document.createElement('td');          // TABLE DEFINITION.
                    td = tr.insertCell(c);
                    if (row[arrHead[c]] != null) {
                        td.append(row[arrHead[c]])
                    } else {
                        td.append('')
                    }

                }
                tr.addEventListener("contextmenu", function (event) {
                    event.preventDefault();
                    currentGSE = event.currentTarget.id;
                    localStorage.setItem('objectToPass', currentGSE);
                    var contextElement = document.getElementById("contextMenu");
                    contextElement.style.top = event.offsetY + "px";
                    contextElement.style.left = event.offsetX + "px";
                });
            }

        }
    });
}

function setGSE() {
    $('#contextMenu').css('display', 'none');
    value = localStorage['objectToPass'];
    $.ajax({
        url: '/GetGSEData',
        data: {
            'type': value
        },
        dataType: 'json',
        success: function (response) {
            var details = response[0]
            $('#GSE').val(details['GSE']);
            $('#Year').val(details['Year']);
            $('#Subject').val(details['Subject']);
            $('#Organ').val(details['Organ']).attr('selected', 'selected');
            $('#Source').val(details['Source']).attr('selected', 'selected');
            $('#Samples').val(details['Samples']);
            $('#Assay').val(details['Assay']).attr('selected', 'selected');
            $('#Platform').val(details['Platform']);
            $('#Title').val(details['Title']);
            $('#URL').val(details['URL']);
            $('#Public').val(details['Public_Notes']);
            $('#Private').val(details['Private_Notes']);
        }
    });
    $('#myModal').css('display', 'block');
    localStorage.removeItem('objectToPass');
}


function rightClick(e) {
    e.preventDefault();
    var menu = document.getElementById("contextMenu")
    menu.style.display = 'block';
    menu.style.left = e.pageX + "px";
    menu.style.top = e.pageY + "px";
    // return false;
}

function deletegse(event) {
    event.preventDefault();
    var gse = document.getElementById("GSE").value;
    // urls = "{% url 'DeleteGSE' GSE="+gse+" %}";
    $.ajax({
        url: "/DeleteGSE",
        type: "GET",
        // url : urls,
        data: {
            GSE: gse
        },
        success: function (response) {
            $('#Cancel').click()
        }
    });
}

function savedata() {
    dict = {}
    var gse = document.getElementById("GSE").value;
    dict['GSE'] = gse;
    var years = document.getElementById("Year").value;
    dict['Year'] = years;
    var samples = document.getElementById("Samples").value;
    dict['Samples'] = samples;
    var subject = document.getElementById("Subject").value;
    dict['Subject'] = subject;
    var platform = document.getElementById("Platform").value;
    dict['Platform'] = platform;
    var url = document.getElementById("URL").value;
    dict['URL'] = url;
    var Title = document.getElementById("Title").value;
    dict['Title'] = Title;
    var pubnotes = document.getElementById("Public").value;
    dict['Public'] = pubnotes;
    var prnotes = document.getElementById("Private").value;
    dict['Private'] = prnotes;
    var source = document.getElementById("Source");
    var sourcetext = source.options[source.options.selectedIndex].text;
    dict['Source'] = sourcetext;
    var organ = document.getElementById("Organ");
    var organtext = organ.options[organ.options.selectedIndex].text;
    dict['Organ'] = organtext;
    var assay = document.getElementById("Assay");
    var assaytext = assay.options[assay.options.selectedIndex].text;
    dict['Assay'] = assaytext;

    $.ajax({
        url: "/SaveGSEData",
        dataType: 'json',
        data: {
            data: dict
        },
        success: function (response) {
            $('#Cancel').click()
        }

    });
}

function getDatafromDB(event) {
    var gsevalue = localStorage['objectToPass'];
    var tablename = event.currentTarget.id;
    $.ajax({
        url: '/GetDatafromDB',
        data: {
            GSE: gsevalue,
            table: tablename
        },
        success: function (response) {
            $('#selectquery').val(response[2])
            cols = response[1]
            rows = response[0]
            BuildTable(cols, rows)
        }
    });
}

function BuildTable(columns, rows) {
    var div = document.getElementById('Database');
    if (div.childElementCount > 0) {
        div.querySelectorAll('*').forEach(n => n.remove());
    }

    var table = document.createElement('Table');
    table.id = 'DBTable'
    table.className = 'table table-bordered table-hover w-50'
    table.style.marginLeft = '0px !important'
    var tr = table.insertRow(-1);

    $.each(columns, function (i, value) {
        var th = document.createElement('th')
        th.setAttribute('class', 'w-auto'); // the header object.
        th.innerHTML = value;
        tr.appendChild(th);
    });

    var rowCnt = table.rows.length;    // get the number of rows.

    $.each(rows, function (i, row) {
        var tr = table.insertRow(rowCnt);
        $.each(row, function (i, value) {
            var td = document.createElement('td');          // TABLE DEFINITION.
            td = tr.insertCell(i);
            td.append(value)
        });
    });

    div.appendChild(table);
    $('#DBCont').css('display', 'block');
    $('#contextMenu').css('display', 'none');


}

// Modeling
function SelectAll() {
    var checkboxes = document.getElementsByClassName('checkitem');
    for (box of checkboxes) {
        if (box.checked) {
            box.checked = false
        } else {
            box.checked = true
        }
    }
}

function getValues(event) {

    var colname = event.currentTarget.value;

    var select = document.getElementById('Values')
    // var select = document.getElementById("DropList")
    var options = select;
    for (i = options.length - 1; i >= 1; i--) {
        select.removeChild(options[i])
    }


    $.ajax({
        url: '/dynamic_dropdown',
        data: {
            'col': colname
        },
        dataType: 'json',
        success: function (response) {
            var colvalues = response;
            var select = document.getElementById('Values')
            for (i = 0; i < colvalues.length; i++) {
                var option = document.createElement('option')
                option.setAttribute('value', colvalues[i])
                option.text = colvalues[i]
                select.appendChild(option)
            }
        }
    });
}

function model_generate() {

    var target = document.getElementById('target')
    var out = target.options[target.selectedIndex].text;

    var unchecked = []
    var inputs = document.querySelectorAll('.checkitem');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked == false) {
            unchecked.push(inputs[i].value)
        }
    }
    $.ajax({
        url: '/get_model_params',
        data: {
            'y': out,
            'x': unchecked
        },
        dataType: 'json',
        success: function (response) {
            alert('Accuracy = ' + response * 100 + '%')
        },
        complete:function(){
            $.ajax({
                    url: '/evaluation',
                    type: "GET",
                    data: {
                        'mode': 'classification',
                        'type': 'render',
                        'csrfmiddlewaretoken': "{{ csrf_token }}"
                    },
                    dataType: "json",
                    success:function(result) {
                        console.log("Evaluation Success. Rendering HTML")
                        $("#evaluationData").html(result["Evaluation"])
                        $("#modelData").hide()
                        $("#evaluationData").show()
                        $("#ConfusionMatrix").html(result["ConfusionMatrix"])
                        $("#StatsTable").html(result["StatisticsTable"])
                        $("#DecileChart").html(result["DecileTable"])
                        $("#ConfusionMatrix").show()
                        $("#StatsTable").show()
                        $("#DecileChart").show()

                    },
                    error:function(error) {
                        console.log("Error" + JSON.stringify(error))
                        alert("Failed to load evaluation. Please refresh and try again.")
                    },

                });
        }
    });
}

function model_generate_reg() {

    var target = document.getElementById('target')
    var out = target.options[target.selectedIndex].text;

    var unchecked = []
    var inputs = document.querySelectorAll('.checkitem');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked == false) {
            unchecked.push(inputs[i].value)
        }
    }
    $.ajax({
        url: '/reg_model_params',
        data: {
            'y': out,
            'x': unchecked
        },
        dataType: 'json',
        success: function (response) {
            alert('MAE =  ' + response[0] + ' RMSE =  ' + response[1] + ' RMSLE = ' + response[2])
        },
        complete:function(){
            $.ajax({
                    url: '/evaluation',
                    type: "GET",
                    data: {
                        'mode': 'regression',
                        'type': 'render',
                        'csrfmiddlewaretoken': "{{ csrf_token }}"
                    },
                    dataType: "json",
                    success:function(result) {
                        console.log("Evaluation Success. Rendering HTML")
                        $("#evaluationData").html(result["Evaluation"])
                        $("#modelData").hide()
                        $("#evaluationData").show()
                        $("#ConfusionMatrix").html(result["ConfusionMatrix"])
                    },
                    error:function(error) {
                        console.log("Error" + JSON.stringify(error))
                        alert("Failed to load evaluation. Please refresh and try again.")
                    },

                });
        }
    });

}

function opentrain(event) {
    $('#fileToUpload').click();
}

function opentest(event) {
    $('#fileToUpload1').click()
}

function settraintext(event) {
    $('#Trainpath').val(event.currentTarget.files[0].name);
}

function settesttext(event) {
    $('#Testpath').val(event.currentTarget.files[0].name);
    $('#submit').click()
    // event.currentTarget.parentElement
}

function renderExploration(){
	var form = document.createElement('form');
	form.method = "GET";
	form.action = "exploration";
	form.style.display = "none";

	var inp = document.createElement("input");
	inp.value = localStorage['objectToPass'];
	inp.name = "gse_value";

	form.appendChild(inp);
	document.body.appendChild(form);
	form.submit();
}
