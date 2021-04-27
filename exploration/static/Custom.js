document.oncontextmenu = rightClick;
var currentGSE=''
function openNotes(evt, notetype) {
          var i, tablinks;
          tablinks = document.getElementsByClassName("tablinks");
          for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");          }
          evt.currentTarget.className += " active";
          PublicNotes = document.getElementById('Public');
          PrivateNotes= document.getElementById('Private');
          if(notetype=="Public"){
              PublicNotes.style.display="block";
              PrivateNotes.style.display="none";
          }
          else {
              PublicNotes.style.display="none";
              PrivateNotes.style.display="block";
          }
        }

function SelectAll() {
    var checkboxes = document.getElementsByClassName('checkitem');
    for (box of checkboxes){
        if(box.checked)
        {
            box.checked="False"
        }
        else
        {
            box.checked="True"
        }

    }
}

function LoadData() {
    // var data = $('GSEData');
    $.ajax({
        url: '/GetGSEData',
        // data: {
        //   'username': username
        // },
        dataType: 'json',
        success: function (response) {
            var arrHead = new Array();
            arrHead = ['GSE', 'Year', 'Subject', 'Organ', 'Source','Samples','Assay','Platform','Title'];
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

            for (var i=0; i<response.length; i++){
                row = response[i]
                var tr = empTable.insertRow(rowCnt); // table row.
                tr.setAttribute('id',row[arrHead[0]])
                // tr.addEventdictener(oncontextmenu,rightClick($('tr')))

                for (var c = 0; c < Object.keys(row).length; c++) {
                    var td = document.createElement('td');          // TABLE DEFINITION.
                    td = tr.insertCell(c);
                    td.append(row[arrHead[c]])
                }
                tr.addEventListener("contextmenu",function(event){
                      event.preventDefault();
                      currentGSE = event.currentTarget.id;
                      localStorage.setItem( 'objectToPass', currentGSE );
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
    $('#myModal').css('display','block');
    $('#GSE').val(localStorage['objectToPass']);
    localStorage.removeItem( 'objectToPass' );
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
    var gse= document.getElementById("GSE").value;
    // urls = "{% url 'DeleteGSE' GSE="+gse+" %}";
    $.ajax({
        url: "/DeleteGSE",
        type: "GET",
        // url : urls,
        data:{
            GSE: gse
        },
        success: function (response) {
            $('#Cancel').click()
        }
    });
}

function savedata(){
    dict={}
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
    var sourcetext= source.options[source.options.selectedIndex].text;
    dict['Source'] = sourcetext;
    var organ = document.getElementById("Organ");
    var organtext= organ.options[organ.options.selectedIndex].text;
    dict['Organ'] = organtext;
    var assay = document.getElementById("Assay");
    var assaytext= assay.options[assay.options.selectedIndex].text;
    dict['Assay'] = assaytext;

    $.ajax({
        url: "/SaveGSEData",
        dataType: 'json',
        data: {
            data : dict
        },
        success: function (response) {
           $('#Cancel').click()
        }

    });
}

function getDatafromDB(event){
    var gsevalue = localStorage['objectToPass'];
    var tablename = event.currentTarget.id;
    $.ajax({
        url: '/GetDatafromDB',
        data:{
            GSE: gsevalue,
            table:tablename
        },
        success: function (response) {
            $('#selectquery').val(response[2])
            cols= response[1]
            rows= response[0]
            BuildTable(cols,rows)
        }
    });
}

function  BuildTable(columns, rows) {
    var div = document.getElementById('Database');
    if(div.childElementCount>0){
       div.querySelectorAll('*').forEach(n => n.remove());
    }

    var table= document.createElement('Table');
    table.id = 'DBTable'
    table.className='table table-bordered table-hover w-50'
    table.style.marginLeft='0px !important'
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
        $.each(row, function(i,value){
            var td = document.createElement('td');          // TABLE DEFINITION.
            td = tr.insertCell(i);
            td.append(value)
        });
    });

    div.appendChild(table);
    $('#DBCont').css('display','block');
    $('#contextMenu').css('display', 'none');
    $('body').css('opacity','0.2')

}


