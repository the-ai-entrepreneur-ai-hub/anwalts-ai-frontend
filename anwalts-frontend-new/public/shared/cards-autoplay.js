document.addEventListener('DOMContentLoaded', function(){
  try{
    document.querySelectorAll('.display-grid.autoplay').forEach(function(group){
      var cards = Array.from(group.querySelectorAll('.display-card'));
      if (!cards || cards.length < 2) return;
      var idx = 0; var paused = false;
      function setActive(i){ cards.forEach(function(c,k){ c.classList.toggle('dc-active', k===i); }); }
      setActive(0);
      var id = setInterval(function(){ if (!paused){ idx = (idx + 1) % cards.length; setActive(idx); } }, 2400);
      group.addEventListener('mouseenter', function(){ paused = true; });
      group.addEventListener('mouseleave', function(){ paused = false; });
    });
  }catch(e){ console && console.warn && console.warn('cards-autoplay init failed', e); }
});
