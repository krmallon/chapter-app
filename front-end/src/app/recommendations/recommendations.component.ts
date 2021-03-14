import { Component, OnInit } from '@angular/core';
import { RecommendationService } from '../services/recommendation.service';

@Component({
  selector: 'app-recommendations',
  templateUrl: './recommendations.component.html',
  styleUrls: ['./recommendations.component.scss']
})
export class RecommendationsComponent implements OnInit {

  constructor(public recommendationService: RecommendationService) { }

  ngOnInit(): void {
    this.recommendationService.getRecommendations('9')
    // this.recommendationService.getRecommendations(sessionStorage.user_id)
  }

}