import Vue from 'vue'
import VueRouter from 'vue-router'
import BoardMemberAdd from '@/mgmt/BoardMemberAdd.vue'
import BoardMemberEdit from '@/mgmt/BoardMemberEdit.vue'
import BoardMemberList from '@/mgmt/BoardMemberList.vue'
import BoardRoleAdd from '@/mgmt/BoardRoleAdd.vue'
import BoardRoleEdit from '@/mgmt/BoardRoleEdit.vue'
import BoardRoleList from '@/mgmt/BoardRoleList.vue'
import FileAdd from '@/mgmt/FileAdd.vue'
import FileEdit from '@/mgmt/FileEdit.vue'
import FileList from '@/mgmt/FileList.vue'
import PageAdd from '@/mgmt/PageAdd.vue'
import PageEdit from '@/mgmt/PageEdit.vue'
import PageList from '@/mgmt/PageList.vue'
import Login from '@/mgmt/Login.vue'


Vue.use(VueRouter);

const router = new VueRouter({
  routes: [
    {path: '/mgmt/boardmember/add', component: BoardMemberAdd},
    {path: '/mgmt/boardmember/edit/:id', component: BoardMemberEdit},
    {path: '/mgmt/boardmember/list', component: BoardMemberList},
    {path: '/mgmt/boardrole/add', component: BoardRoleAdd},
    {path: '/mgmt/boardrole/edit/:id', component: BoardRoleEdit},
    {path: '/mgmt/boardrole/list', component: BoardRoleList},
    {path: '/mgmt/file/add', component: FileAdd},
    {path: '/mgmt/file/edit/:id', component: FileEdit},
    {path: '/mgmt/file/list', component: FileList},
    {path: '/mgmt/page/list', component: PageList},
    {path: '/mgmt/page/add', component: PageAdd},
    {path: '/mgmt/page/edit/:id', component: PageEdit},
    {path: '/mgmt/login', component: Login},
    {path: '*', redirect: '/mgmt/page/list'},
  ],
  mode: 'history'
});

export default router