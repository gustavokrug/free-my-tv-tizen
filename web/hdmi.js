/* Local HDMI names and pictures. The source is changed only by the home screen's explicit launch action. */
(function () {
  'use strict';
  var choices = [['hdmi', 'HDMI'], ['switch2', 'Switch 2'], ['wiiu', 'Wii U'], ['ps5', 'PS5'], ['steamdeck', 'Steam Deck']];
  var defaults = {hdmi1: {name: 'Switch 2', icon: 'switch2'}, hdmi2: {name: 'Wii U', icon: 'wiiu'}, hdmi3: {name: 'PS5', icon: 'ps5'}, hdmi4: {name: 'Steam Deck', icon: 'steamdeck'}};
  var saved = {}, overlay = null, input = null, pick = 0, active = null, controls = [], focus = 0;
  var hold = null, held = false, consumed = false, storageKey = 'fmtv.hdmi.v1';
  try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (e) {}
  function match(name) {
    if (/playstation\s*5|ps5/i.test(name)) return 'ps5';
    if (/switch\s*2/i.test(name)) return 'switch2';
    if (/wii\s*u/i.test(name)) return 'wiiu';
    if (/steam\s*deck/i.test(name)) return 'steamdeck';
    return 'hdmi';
  }
  function details(source) {
    var custom = saved[source.key], nativeName = source.deviceName || '';
    if (custom && custom.name && /^(hdmi|switch2|wiiu|ps5|steamdeck)$/.test(custom.icon)) return custom;
    if (nativeName && !/^HDMI\s*\d*$/i.test(nativeName)) return {name: nativeName, icon: match(nativeName)};
    return defaults[source.key] || {name: source.label, icon: 'hdmi'};
  }
  function close() {
    if (overlay) overlay.parentNode.removeChild(overlay);
    overlay = null;
    if (window.HDMIHost) HDMIHost.redraw();
  }
  function button(label, action) {
    var node = document.createElement('button');
    node.textContent = label;
    node.onclick = action;
    controls.push(node);
    return node;
  }
  function setFocus(index) {
    focus = Math.max(0, Math.min(controls.length - 1, index));
    controls[focus].focus();
  }
  function open(source) {
    if (!source || overlay) return;
    active = source;
    var value = details(source);
    overlay = document.createElement('div');
    overlay.className = 'hdmi-editor';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-label', 'Editar ' + source.label);
    var box = document.createElement('div');
    box.className = 'hdmi-box';
    var title = document.createElement('h2');
    title.textContent = 'Editar dispositivo — ' + source.label;
    box.appendChild(title);
    var hint = document.createElement('p');
    hint.textContent = 'Escolha uma imagem e edite o nome. Voltar cancela.';
    box.appendChild(hint);
    var presets = document.createElement('div');
    presets.className = 'hdmi-presets';
    controls = [];
    choices.forEach(function (choice, index) {
      var b = button(choice[1], function () {
        pick = index;
        input.value = choice[1];
        mark();
      });
      if (choice[0] !== 'hdmi') {
        var img = document.createElement('img');
        img.src = 'icons/home-' + choice[0] + '.png';
        b.insertBefore(img, b.firstChild);
      }
      if (choice[0] === value.icon) pick = index;
      presets.appendChild(b);
    });
    box.appendChild(presets);
    var label = document.createElement('label');
    label.textContent = 'Nome do dispositivo';
    input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 40;
    input.value = value.name;
    label.appendChild(input);
    box.appendChild(label);
    controls.push(input);
    var error = document.createElement('p');
    error.className = 'hdmi-error';
    box.appendChild(error);
    box.appendChild(button('Salvar', function () {
      var name = input.value.replace(/^\s+|\s+$/g, '');
      if (!name) { error.textContent = 'Informe um nome para o dispositivo.'; setFocus(5); return; }
      var next = {};
      for (var key in saved) if (Object.prototype.hasOwnProperty.call(saved, key)) next[key] = saved[key];
      next[active.key] = {name: name, icon: choices[pick][0]};
      try { localStorage.setItem(storageKey, JSON.stringify(next)); }
      catch (e) { error.textContent = 'Não foi possível salvar. Tente novamente.'; return; }
      saved = next;
      close();
    }));
    box.appendChild(button('Cancelar', close));
    overlay.appendChild(box);
    document.getElementById('stage').appendChild(overlay);
    mark();
    setFocus(pick);
  }
  function mark() {
    for (var i = 0; i < 5; i++) controls[i].className = i === pick ? 'selected' : '';
  }
  function stop(e) { e.preventDefault(); e.stopImmediatePropagation(); }
  function keydown(e) {
    var k = e.keyCode;
    if (overlay) {
      if (k === 10009 || k === 27 || (k === 8 && document.activeElement !== input)) { close(); stop(e); return true; }
      var index = controls.indexOf(document.activeElement);
      if (index >= 0) focus = index;
      if (k === 37 || k === 39 || k === 38 || k === 40) {
        if (document.activeElement === input && (k === 37 || k === 39)) return true;
        setFocus(focus + (k === 37 || k === 38 ? -1 : 1)); stop(e);
      } else if (k === 13 && document.activeElement !== input) { controls[focus].click(); stop(e); }
      return true;
    }
    var source = window.HDMIHost && HDMIHost.selected();
    if (!source) return false;
    if (k === 10252 || k === 415 || k === 19) { open(source); stop(e); return true; }
    if (k === 13) {
      if (!held) {
        held = true; consumed = false;
        hold = setTimeout(function () { consumed = true; open(source); }, 650);
      }
      stop(e); return true;
    }
    return false;
  }
  document.addEventListener('keyup', function (e) {
    if (e.keyCode !== 13 || !held) return;
    clearTimeout(hold); held = false;
    if (!consumed && !overlay && window.HDMIHost) HDMIHost.activate();
    stop(e);
  });
  window.addEventListener('blur', function () { clearTimeout(hold); held = false; });
  try { if (window.tizen && tizen.tvinputdevice) tizen.tvinputdevice.registerKey('MediaPlayPause'); } catch (e) {}
  window.HDMI = {details: details, open: open, close: close, keydown: keydown, isOpen: function () { return !!overlay; }};
})();
