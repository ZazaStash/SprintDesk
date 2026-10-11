const $ = (id) => document.getElementById(id);
const state = {token: localStorage.getItem('sd-token'), user: null, users: [], tasks: [], editing: null, authMode: 'login'};
const statusNames = {todo:'К выполнению',in_progress:'В процессе',done:'Готово'};
const priorityNames = {1:'Низкий',2:'Средний',3:'Высокий'};
let toastTimer;

function toast(message) {
  const node = $('toast');
  node.textContent = message;
  node.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove('visible'), 3200);
}

async function request(path, options = {}) {
  const headers = {...(options.body ? {'Content-Type':'application/json'} : {}), ...(state.token ? {'Authorization':`Bearer ${state.token}`} : {})};
  const response = await fetch(path, {...options, headers});
  if (response.status === 204) return null;
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof result.detail === 'string' ? result.detail : (Array.isArray(result.detail) ? result.detail[0]?.msg : 'Ошибка соединения');
    if (response.status === 401 && !path.includes('/auth/login')) showAuth();
    throw new Error(detail || 'Не удалось выполнить запрос');
  }
  return result;
}

function setAuthMode(mode) {
  state.authMode = mode;
  $('tab-login').classList.toggle('active',mode==='login');
  $('tab-register').classList.toggle('active',mode==='register');
  $('name-field').classList.toggle('hidden',mode!=='register');
  $('auth-name').required = mode==='register';
  $('auth-password').autocomplete = mode==='login'?'current-password':'new-password';
  $('auth-submit').innerHTML = mode==='login'?'Войти в пространство <span>↗</span>':'Создать аккаунт <span>↗</span>';
}

function showAuth() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('sd-token');
  $('app-view').classList.add('hidden');
  $('auth-view').classList.remove('hidden');
}

async function enterApp() {
  state.user = await request('/api/auth/me');
  $('auth-view').classList.add('hidden');
  $('app-view').classList.remove('hidden');
  const initial = state.user.name.slice(0,1).toUpperCase();
  $('side-name').textContent = state.user.name;
  $('side-role').textContent = state.user.role === 'admin'?'Администратор':'Участник';
  $('side-avatar').textContent = initial;
  $('top-avatar').textContent = initial;
  if (state.user.role === 'admin') {
    state.users = await request('/api/users');
    $('owner-field').classList.remove('hidden');
    $('task-owner').replaceChildren(...state.users.map(u => {const option = document.createElement('option');option.value=u.id;option.textContent=`${u.name} (${u.email})`;return option;}));
  } else {
    $('owner-field').classList.add('hidden');
    state.users = [state.user];
  }
  await loadTasks();
}

async function loadTasks() {
  state.tasks = await request('/api/tasks');
  render();
}

function render() {
  const tasks = state.tasks;
  const complete = tasks.filter(t => t.status==='done').length;
  const progress = tasks.filter(t => t.status==='in_progress').length;
  $('stat-total').textContent = tasks.length;
  $('stat-progress').textContent = progress;
  $('stat-done').textContent = complete;
  $('stat-percent').textContent = `${tasks.length?Math.round(100*complete/tasks.length):0}%`;
  $('progress-fill').style.width = `${tasks.length?100*complete/tasks.length:0}%`;
  const q = $('search').value.trim().toLowerCase();
  const priority = $('priority-filter').value;
  const filtered = tasks.filter(t=>(t.title+' '+t.description).toLowerCase().includes(q)&&(priority==='all'||String(t.priority)===priority));
  $('task-counter').textContent = filtered.length;
  for (const status of Object.keys(statusNames)) {
    const columnTasks = filtered.filter(t => t.status===status);
    $('count-'+status).textContent = columnTasks.length;
    const container = $('column-'+status);
    container.replaceChildren();
    if (!columnTasks.length) {
      const empty = document.createElement('div');
      empty.className='empty-column';
      const ornament = document.createElement('span');
      ornament.textContent='◇';
      empty.append(ornament,document.createTextNode('Пока здесь нет задач'));
      container.append(empty);
      continue;
    }
    for (const task of columnTasks) container.append(renderTask(task));
  }
}

function renderTask(task) {
  const card = document.createElement('article');
  card.className='task-card';
  card.tabIndex=0;
  card.setAttribute('role','button');
  const top=document.createElement('div');top.className='task-card-top';
  const priority=document.createElement('span');priority.className=`priority-pill ${task.priority===3?'high':task.priority===2?'medium':'low'}`;priority.textContent=priorityNames[task.priority];
  const number=document.createElement('span');number.className='task-number';number.textContent='#'+String(task.id).padStart(3,'0');
  top.append(priority,number);
  const title=document.createElement('h3');title.textContent=task.title;
  const description=document.createElement('p');description.textContent=task.description||'Без описания';
  const bottom=document.createElement('div');bottom.className='task-bottom';
  const date=document.createElement('small');date.textContent=new Date(task.created_at).toLocaleDateString('ru-RU',{day:'numeric',month:'short',year:'numeric'});
  const avatar=document.createElement('span');avatar.className='task-avatar';avatar.title=state.users.find(u=>u.id===task.owner_id)?.name||'Участник';avatar.textContent=(state.users.find(u=>u.id===task.owner_id)?.name||'У').slice(0,1).toUpperCase();
  bottom.append(date,avatar);card.append(top,title,description,bottom);
  card.addEventListener('click',()=>openTask(task));
  card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();openTask(task);}});
  return card;
}

function openTask(task=null) {
  state.editing=task;
  $('task-form').reset();
  $('modal-title').textContent=task?'Редактировать задачу':'Новая задача';
  $('delete-task').classList.toggle('hidden',!task);
  $('task-title').value=task?.title||'';
  $('task-description').value=task?.description||'';
  $('task-status').value=task?.status||'todo';
  $('task-priority').value=task?.priority||2;
  $('task-owner').value=task?.owner_id||state.user.id;
  $('task-modal').showModal();
  $('task-title').focus();
}

$('tab-login').addEventListener('click',()=>setAuthMode('login'));
$('tab-register').addEventListener('click',()=>setAuthMode('register'));
$('auth-form').addEventListener('submit',async event=>{
  event.preventDefault();
  const payload={email:$('auth-email').value,password:$('auth-password').value};
  if(state.authMode==='register')payload.name=$('auth-name').value;
  const submit=$('auth-submit');submit.disabled=true;
  try{
    const data=await request('/api/auth/'+(state.authMode==='login'?'login':'register'),{method:'POST',body:JSON.stringify(payload)});
    state.token=data.access_token;
    localStorage.setItem('sd-token',state.token);
    await enterApp();
    toast('Добро пожаловать в SprintDesk!');
  }catch(error){toast(error.message);}finally{submit.disabled=false;}
});
$('logout').addEventListener('click',showAuth);
$('new-task').addEventListener('click',()=>openTask());
$('close-modal').addEventListener('click',()=> $('task-modal').close());
$('cancel-modal').addEventListener('click',()=> $('task-modal').close());
$('search').addEventListener('input',render);
$('priority-filter').addEventListener('change',render);
$('task-form').addEventListener('submit',async event=>{
  event.preventDefault();
  const payload={title:$('task-title').value,description:$('task-description').value,status:$('task-status').value,priority:Number($('task-priority').value)};
  if(state.user.role==='admin')payload.owner_id=Number($('task-owner').value);
  const isEdit=Boolean(state.editing);
  const id=state.editing?.id;
  $('save-task').disabled=true;
  try{
    await request(isEdit?`/api/tasks/${id}`:'/api/tasks',{method:isEdit?'PATCH':'POST',body:JSON.stringify(payload)});
    $('task-modal').close();await loadTasks();toast(isEdit?'Задача обновлена':'Задача создана');
  }catch(error){toast(error.message);}finally{$('save-task').disabled=false;}
});
$('delete-task').addEventListener('click',async()=>{
  if(!state.editing||!confirm('Удалить задачу?'))return;
  try{await request(`/api/tasks/${state.editing.id}`,{method:'DELETE'});$('task-modal').close();await loadTasks();toast('Задача удалена');}catch(error){toast(error.message);}
});
if(state.token){enterApp().catch(()=>showAuth());}
