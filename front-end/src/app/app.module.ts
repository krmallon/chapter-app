import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { MDBBootstrapModule } from 'angular-bootstrap-md';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { RouterModule } from '@angular/router';
import { NavComponent } from './nav/nav.component';
import { BookComponent } from './book/book.component';
import { ProfileComponent } from './profile/profile.component';
import { NotfoundComponent } from './notfound/notfound.component';
import { UserService } from './services/user.service';
import { AuthService } from './auth.service';
import { HttpClientModule } from '@angular/common/http';
import { BookService } from './services/book.service';
import { RecommendationsComponent } from './recommendations/recommendations.component';

var routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'user/:id',
    component: ProfileComponent
  },
  {
    path: 'recommendations',
    component: RecommendationsComponent
  },
  {
    path: 'books/:id',
    component: BookComponent
  },
  {
    path: '404',
    component: NotfoundComponent
  },
  {
    path: '**',
    redirectTo: '/404'
  }
]

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    NavComponent,
    BookComponent,
    ProfileComponent,
    NotfoundComponent,
    RecommendationsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    RouterModule.forRoot(routes),
    MDBBootstrapModule.forRoot(),
    HttpClientModule
  ],
  providers: [UserService, AuthService, BookService],
  bootstrap: [AppComponent]
})
export class AppModule { }
