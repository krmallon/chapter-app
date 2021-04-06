import { HttpClientModule } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AppRoutingModule } from '../app-routing.module';

import { CommentService } from './comment.service';

describe('CommentService', () => {
  let service: CommentService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppRoutingModule,
        HttpClientModule
      ]
    });
    service = TestBed.inject(CommentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
