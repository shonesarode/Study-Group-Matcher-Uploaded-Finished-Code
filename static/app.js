'use strict';
const selected = { courses: new Set(['ECE 406']), slots: new Set(['Mon 5pm']), goals: new Set(['exam review']) };
let lastProfile = null;
const $ = id => document.getElementById(id);

function addChipGroup(id, options) {
  const parent = $(id);
  options.forEach(label => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'chip';
    button.textContent = label;
    button.setAttribute('aria-pressed', selected[id].has(label) ? 'true' : 'false');
    button.addEventListener('click', () => {
      const set = selected[id];
      if (set.has(label)) set.delete(label);
      else if (id !== 'courses' || set.size < 4) set.add(label);
      button.classList.toggle('active', set.has(label));
      button.setAttribute('aria-pressed', String(set.has(label)));
    });
    button.classList.toggle('active', selected[id].has(label));
    parent.appendChild(button);
  });
}

async function request(path, profile) {
  const result = await fetch(path, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(profile) });
  const body = await result.json();
  if (!result.ok) {
    const detail = typeof body.detail === 'string' ? body.detail : 'Please check your information.';
    throw new Error(detail);
  }
  return body;
}

function profile() {
  return {
    alias: $('alias').value.trim(), courses:[...selected.courses],
    slots:[...selected.slots], mode:$('mode').value, goals:[...selected.goals],
  };
}
function showMatches(items) {
  const container = $('matches');
  container.replaceChildren();
  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.textContent = 'No compatible demo profiles. Try a different time, course or format.';
    container.appendChild(empty);
    return;
  }
  items.forEach(item => {
    const card = document.createElement('div'); card.className = 'match';
    const avatar = document.createElement('div'); avatar.className = 'avatar'; avatar.textContent = item.alias.charAt(0);
    const body = document.createElement('div'); body.className = 'match-body';
    const name = document.createElement('strong'); name.textContent = item.alias;
    const description = document.createElement('p'); description.textContent = item.why + ' · ' + item.mode;
    const tags = document.createElement('div'); tags.className = 'tags';
    [...item.shared_courses, ...item.shared_slots].forEach(value => {
      const tag = document.createElement('span'); tag.textContent = value; tags.appendChild(tag);
    });
    const score = document.createElement('span'); score.className = 'score'; score.textContent = item.score + ' pts';
    body.append(name, description, tags); card.append(avatar, body, score);
    container.appendChild(card);
  });
}

async function initialize() {
  try {
    const response = await fetch('/api/options');
    if (!response.ok) throw new Error('options request failed');
    const options = await response.json();
    addChipGroup('courses', options.courses);
    addChipGroup('slots', options.slots);
    addChipGroup('goals', options.goals);
  } catch {
    $('message').textContent = 'Could not load the demo. Check that the API is running.';
  }
}
$('matcher').addEventListener('submit', async event => {
  event.preventDefault(); $('message').textContent = '';
  const input = profile();
  if (!input.courses.length || !input.slots.length || !input.goals.length) {
    $('message').textContent = 'Choose at least one course, time and goal.'; return;
  }
  try {
    const response = await request('/api/matches', input);
    lastProfile = input;
    showMatches(response.recommendations);
    $('group-button').disabled = !response.recommendations.length;
    $('group-result').textContent = '';
  } catch (error) { $('message').textContent = error.message; }
});
$('group-button').addEventListener('click', async () => {
  if (!lastProfile) return;
  try {
    const group = await request('/api/group', lastProfile);
    $('group-result').textContent = `Suggested group: ${group.members.join(' + ')}. Shared time: ${group.common_slots.join(', ') || 'none'}.`;
  } catch (error) { $('group-result').textContent = error.message; }
});
initialize();
