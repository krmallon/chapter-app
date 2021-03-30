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
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FeedComponent } from './feed/feed.component';
import { MessagesComponent } from './messages/messages.component';
import { SearchComponent } from './search/search.component';
import { GroupComponent } from './group/group.component';
import { GroupsComponent } from './groups/groups.component';
import { GoalService } from './services/goal.service';
import { GroupService } from './services/group.service';
import { ReviewService } from './services/review.service';
import { CommentService } from './services/comment.service';
import { AchievementService } from './services/achievement.service';
import { MessagingService } from './services/messaging.service';
import { SearchService } from './services/search.service';

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
    path: 'search/:query',
    component: SearchComponent
  },
  {
    path: 'feed',
    component: FeedComponent
  },
  {
    path: 'messages',
    component: MessagesComponent
  },
  {
    path: 'groups',
    component: GroupsComponent
  }, 
  {
    path: 'group/:id',
    component: GroupComponent
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
    FeedComponent,
    MessagesComponent,
    SearchComponent,
    GroupComponent,
    GroupsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    RouterModule.forRoot(routes),
    MDBBootstrapModule.forRoot(),
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule
  ],
  providers: [
    UserService, AuthService, BookService, GoalService, GroupService,
    ReviewService, CommentService, AchievementService, MessagingService,
    SearchService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
