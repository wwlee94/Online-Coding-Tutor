//최대 글자수 제한
function maxLength(cm, change) {
    var maxLength = cm.getOption("maxLength");
    if (maxLength && change.update) {
        var str = change.text.join("\n");
        var delta = str.length-(cm.indexFromPos(change.to) - cm.indexFromPos(change.from));
        if (delta <= 0) { return true; }
        delta = cm.getValue().length+delta-maxLength;
        if (delta > 0) {
            str = str.substr(0, str.length-delta);
            change.update(change.from, change.to, str.split("\n"));
        }
    }
    return true;
}

//라인수 1개로 제한 타이핑/붙여넣기 포함
function singleLine(cm, changeObj) {
    var typedNewLine = changeObj.origin == '+input' && typeof changeObj.text == "object" && changeObj.text.join("") == "";
    if (typedNewLine) {
        return changeObj.cancel();
    }
    var pastedNewLine = changeObj.origin == 'paste' && typeof changeObj.text == "object" && changeObj.text.length > 1;
    if (pastedNewLine) {
        var newText = changeObj.text.join(" ");
        // trim
        //newText = $.trim(newText);
        return changeObj.update(null, null, [newText]);
    }
    return null;
}

//Python 자동완성 설정!
function pythonHint(editor, input) {
    if (input.text[0] === ';' || input.text[0] === ' ' || input.text[0] === ":") {
        return;
    }
    editor.showHint({
        hint: CodeMirror.pythonHint
    });
}
//breakpoint 설정 !
function breakpoints(cm,n){
   var info = cm.lineInfo(n);
   cm.setGutterMarker(n,"breakpoints",info.gutterMarkers ? null : makeMarker());
}
function makeMarker(type) {
  color = "#30A9DE"
  if(type=='current'){
    color = '#FFFFFF';
  }
  else if(type=='next'){
    color = '#30A9DE';
  }
  // blue : #30A9DE
  // red : #E53A40
  // yellow : #EFDC05
  var marker = document.createElement("div");
  marker.style.color = color;
  marker.style.textAlign = "center";
  marker.innerHTML = "->";
  return marker;
}
