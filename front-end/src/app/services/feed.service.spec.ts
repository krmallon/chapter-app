import { HttpClientModule } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AppRoutingModule } from '../app-routing.module';

import { FeedService } from './feed.service';

describe('FeedService', () => {
  let service: FeedService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppRoutingModule,
        HttpClientModule
      ]
    });
    service = TestBed.inject(FeedService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
