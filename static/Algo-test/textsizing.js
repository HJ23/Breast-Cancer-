      function varitext(text){
           text=document
           print(text)
       }
	   

       var min=8;
       var max=22;
       var i=0;
	   
function increaseFontSize() {
    
     var p = document.getElementsByClassName('resizable-text');
     for (i=0; i<p.length; i++) {
             if(p[i].style.fontSize) {
                var s = parseInt(p[i].style.fontSize.replace("px",""));
             } else {
                var s = 16;
             }
             if(s!=max) {
                s += 1;
             }
             p[i].style.fontSize = s+"px"
          }
       }
	   
       function decreaseFontSize() {
           var p = document.getElementsByClassName('resizable-text');
          for(i=0;i<p.length;i++) {
             if(p[i].style.fontSize) {
                var s = parseInt(p[i].style.fontSize.replace("px",""));
             } else {
                var s = 16;
             }
             if(s!=min) {
                s -= 1;
             }
             p[i].style.fontSize = s+"px"
          }
       }