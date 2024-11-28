import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { authGuard } from './guards/auth.guard';
import { LogoutComponent } from './logout/logout.component';

export const routes: Routes = [
  { 
    path: 'home', 
    component: HomeComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'login', 
    component: LoginComponent 
  },
  { 
    path: '', 
    redirectTo: 'home', 
    pathMatch: 'full' 
  },
  { 
    path: 'logout', 
    component: LogoutComponent,
    canActivate: [authGuard]
  },
  { 
    path: '**', 
    redirectTo: 'home' 
  }
];
