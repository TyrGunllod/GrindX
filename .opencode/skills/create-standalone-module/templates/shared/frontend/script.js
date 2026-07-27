var ICON_CATEGORIES={coding:['fas fa-code','fas fa-terminal','fas fa-bug','fas fa-cog','fas fa-wrench','fas fa-tools','fas fa-laptop-code','fas fa-code-branch','fas fa-tag','fas fa-tags','fas fa-key','fas fa-lock','fas fa-shield-alt','fas fa-database','fas fa-cloud','fas fa-server'],devices:['fas fa-mobile-alt','fas fa-tablet-alt','fas fa-laptop','fas fa-desktop','fas fa-hdd','fas fa-microchip','fas fa-sd-card','fas fa-sim-card','fas fa-plug','fas fa-battery-full','fas fa-wifi'],design:['fas fa-paint-brush','fas fa-palette','fas fa-pencil-alt','fas fa-pen','fas fa-pen-fancy','fas fa-highlighter','fas fa-marker','fas fa-vector-square','fas fa-eye-dropper','fas fa-ruler-combined','fas fa-layer-group','fas fa-eraser','fas fa-th-large','fas fa-th-list','fas fa-archive'],files:['fas fa-folder','fas fa-folder-open','fas fa-folder-plus','fas fa-file','fas fa-file-alt','fas fa-file-invoice','fas fa-file-code','fas fa-file-image','fas fa-file-pdf','fas fa-copy','fas fa-paste','fas fa-save','fas fa-download','fas fa-upload','fas fa-print'],users:['fas fa-user','fas fa-users','fas fa-user-tie','fas fa-user-cog','fas fa-user-circle','fas fa-user-friends','fas fa-user-plus','fas fa-user-check','fas fa-user-shield','fas fa-user-graduate','fas fa-phone','fas fa-envelope','fas fa-comment','fas fa-comment-dots','fas fa-bell']};
function _toggleIconPicker(){var g=document.getElementById('icon-grid');g.style.display=g.style.display==='none'?'block':'none';if(g.style.display!=='block')return;var v=document.getElementById('f-icone').value;g.innerHTML='';Object.keys(ICON_CATEGORIES).forEach(function(c){var cat=document.createElement('div');cat.className='icon-category';cat.textContent=c;g.appendChild(cat);var row=document.createElement('div');row.className='icon-grid-items';ICON_CATEGORIES[c].forEach(function(ic){var it=document.createElement('span');it.className='icon-item';it.innerHTML='<i class=\"'+ic+'\"></i>';it.title=ic;if(v===ic)it.classList.add('selected');it.addEventListener('click',function(){document.getElementById('f-icone').value=ic;document.getElementById('icon-preview').innerHTML='<i class=\"'+ic+'\"></i>';g.style.display='none';});row.appendChild(it);});g.appendChild(row);});}
let modelos=[];let editingId=null;
const _isGrindx=typeof window!=='undefined'&&window.grindx&&window.grindx.session;
const _apiBase=(function(){var h=window.location.hostname,p=window.location.port;if(p==='7080')return'http://'+h+':7000/v1/pop-modelos';if(window.GRINDX_CONFIG?.API_BASE_URL)return window.GRINDX_CONFIG.API_BASE_URL+'/pop-modelos';return'/v1/pop-modelos';})();
const API_BASE=_apiBase;
const API_KEY=localStorage.getItem('popg_api_key')||'';
async function apiFetch(url,options){
 options=options||{};const headers={'Content-Type':'application/json',...(options.headers||{})};
 if(_isGrindx){var tk=window.grindx.session.getToken();if(tk)headers['Authorization']='Bearer '+tk;}
 else if(API_KEY)headers['X-API-Key']=API_KEY;
 var r=await fetch(url,{...options,headers});if(!r.ok){var e={detail:'HTTP '+r.status};try{e=await r.json()}catch(ex){}throw new Error(e.detail||'Erro');}
 return r.status!==204?r.json():null;
}
var api={listar:function(){return apiFetch(API_BASE+'?page_size=100')},criar:function(d){return apiFetch(API_BASE,{method:'POST',body:JSON.stringify(d)})},atualizar:function(i,d){return apiFetch(API_BASE+'/'+i,{method:'PUT',body:JSON.stringify(d)})},excluir:function(i){return apiFetch(API_BASE+'/'+i,{method:'DELETE'})}};
function showToast(m,t){t=t||'success';var c=document.getElementById('toast-container'),to=document.createElement('div');to.className='toast toast-'+t;to.textContent=m;c.appendChild(to);setTimeout(function(){if(to.parentNode)to.remove()},3000);}
function openModal(m){
 editingId=m?m.id:null;document.getElementById('modal-title').textContent=m?'Editar Modelo':'Novo Modelo';
 document.getElementById('form-id').value=m?m.id:'';
 document.getElementById('form-modelo').reset();document.getElementById('secoes-opcionais').innerHTML='';
 if(m){document.getElementById('f-codigo').value=m.codigo||'';document.getElementById('f-prefixo').value=m.prefixo||'';document.getElementById('f-nome').value=m.nome||'';document.getElementById('f-icone').value=m.icone||'fas fa-file-alt';document.getElementById('icon-preview').innerHTML='<i class=\"'+(m.icone||'fas fa-file-alt')+'\"></i>';document.getElementById('f-descricao').value=m.descricao||'';
  for(var i=1;i<=15;i++){var k='sec_name_'+(i<10?'0':'')+i;var v=m[k];if(v)addSecao(i,v);}
 }else{document.getElementById('f-icone').value='fas fa-file-alt';document.getElementById('icon-preview').innerHTML='<i class=\"fas fa-file-alt\"></i>';}
 renderSecVazias();document.getElementById('modal-editor').style.display='flex';
}
function closeModal(){document.getElementById('modal-editor').style.display='none';editingId=null;}
function addSecao(n,v){v=v||'';var c=document.getElementById('secoes-opcionais'),d=document.createElement('div');d.className='secao-opcional-item';d.innerHTML='<span class="secao-num">'+n+'.</span><input type="text" class="form-input secao-input" data-num="'+n+'" maxlength="30" value="'+v.replace(/"/g,'&quot;')+'" placeholder="Secao '+n+'"><button type="button" class="btn-icon secao-clear" aria-label="Limpar">&times;</button>';c.appendChild(d);}
function renderSecVazias(){var c=document.getElementById('secoes-opcionais'),cnt=c.querySelectorAll('.secao-opcional-item').length;if(cnt<3){for(var i=cnt+1;i<=3;i++)addSecao(i);}}
function collectData(){var d={codigo:document.getElementById('f-codigo').value.trim().toUpperCase(),prefixo:document.getElementById('f-prefixo').value.trim(),nome:document.getElementById('f-nome').value.trim(),icone:document.getElementById('f-icone').value.trim()||'fas fa-file-alt',descricao:document.getElementById('f-descricao').value.trim(),objetivo:'Objetivo',escopo:'Escopo'};
 document.querySelectorAll('.secao-input').forEach(function(i){var v=i.value.trim();if(v){var n=parseInt(i.dataset.num);d['sec_name_'+(n<10?'0':'')+n]=v;}});return d;}
async function validateForm(d){var req=['codigo','prefixo','nome','icone','descricao'];var lb={codigo:'Codigo',prefixo:'Prefixo',nome:'Nome',icone:'Icone',descricao:'Descricao'};for(var i=0;i<req.length;i++){if(!d[req[i]]){showToast('Campo obrigatorio: '+(lb[req[i]]||req[i]),'error');return false;}}
 var existing=modelos.find(function(m){return m.codigo===d.codigo&&m.id!==editingId});if(existing){showToast('Codigo "'+d.codigo+'" ja existe','error');return false;}
 return true;}
async function handleSubmit(e){e.preventDefault();var d=collectData();if(!await validateForm(d))return;try{if(editingId){await api.atualizar(editingId,d);showToast('Atualizado');}else{await api.criar(d);showToast('Criado');}closeModal();await load();}catch(err){showToast(err.message,'error');}}
function handleDelete(id){if(!confirm('Excluir?'))return;api.excluir(id).then(function(){showToast('Excluido');load();}).catch(function(err){showToast(err.message,'error');});}
function render(){
 var g=document.getElementById('lista-modelos'),e=document.getElementById('empty-state'),c=document.getElementById('modelo-count');
 if(!modelos||!modelos.length){g.innerHTML='';e.style.display='block';c.textContent='0';return;}
 e.style.display='none';c.textContent=modelos.length;
 g.innerHTML=modelos.map(function(m){return'<article class="modelo-card" data-id="'+m.id+'"><div class="modelo-icon"><i class="'+(m.icone||'fas fa-file-alt')+'"></i></div><div class="modelo-info"><div class="modelo-code">'+m.prefixo+'-'+m.codigo+'</div><div class="modelo-name">'+(m.nome||'')+'</div><div class="modelo-desc">'+(m.descricao||'')+'</div></div><div class="modelo-actions"><button class="btn-icon action-edit" data-id="'+m.id+'" aria-label="Editar">&#9998;</button><button class="btn-icon action-delete" data-id="'+m.id+'" aria-label="Excluir">&#128465;</button></div></article>';}).join('');
}
async function load(){try{var r=await api.listar();modelos=r.items||r;render();}catch(err){showToast('Erro: '+err.message,'error');}}
document.addEventListener('DOMContentLoaded',function(){
 document.getElementById('btn-novo').addEventListener('click',function(){openModal(null);});
 document.getElementById('btn-cancelar').addEventListener('click',closeModal);
 document.getElementById('form-modelo').addEventListener('submit',handleSubmit);
 document.getElementById('lista-modelos').addEventListener('click',function(e){
  var eb=e.target.closest('.action-edit'),db=e.target.closest('.action-delete');
  if(eb){var id=parseInt(eb.dataset.id);var m=modelos.find(function(x){return x.id===id;});if(m)openModal(m);}
  if(db)handleDelete(parseInt(db.dataset.id));
 });
 document.getElementById('secoes-opcionais').addEventListener('click',function(e){
  if(e.target.matches('.secao-clear')){e.target.closest('.secao-opcional-item').remove();}
 });
 document.getElementById('secoes-opcionais').addEventListener('input',function(e){
  if(e.target.matches('.secao-input')){var v=e.target.value.trim(),cb=e.target.parentElement.querySelector('.secao-clear');cb.style.display=v?'':'none';}
 });
 document.getElementById('btn-add-secao').addEventListener('click',function(){var c=document.getElementById('secoes-opcionais'),cnt=c.querySelectorAll('.secao-opcional-item').length;if(cnt<15)addSecao(cnt+1);});
 document.getElementById('modal-editor').addEventListener('click',function(e){if(e.target.id==='modal-editor')closeModal();});
 document.getElementById('btn-pick-icon').addEventListener('click',_toggleIconPicker);
 document.getElementById('f-icone').addEventListener('input',function(){document.getElementById('icon-preview').innerHTML='<i class=\"'+this.value+'\"></i>';});
 document.getElementById('search-input').addEventListener('input',function(e){
  var t=e.target.value.toLowerCase();if(!t){render();return;}
  var f=modelos.filter(function(m){return(m.codigo&&m.codigo.toLowerCase().indexOf(t)>=0)||(m.nome&&m.nome.toLowerCase().indexOf(t)>=0)||(m.prefixo&&m.prefixo.toLowerCase().indexOf(t)>=0);});
  var g=document.getElementById('lista-modelos');if(!f.length){g.innerHTML='<p style="text-align:center;color:var(--text-muted)">Nenhum resultado.</p>';}else{var o=modelos;modelos=f;render();modelos=o;}
 });
 load();
});
