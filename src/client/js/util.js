'use strict';

// from: http://stackoverflow.com/questions/6659351/removing-all-script-tags...
// crude attempt to sanitize some html for display on my site
// TODO(ark) remove all event handlers from all elements too
function stripScripts(s) {
  var div = document.createElement('div');
  div.innerHTML = s;
  var scripts = div.getElementsByTagName('script');
  var i = scripts.length;
  while (i--) {
    scripts[i].parentNode.removeChild(scripts[i]);
  }
  return div.innerHTML;
}
