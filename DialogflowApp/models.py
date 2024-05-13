from django.db import models


class Team(models.Model):
    name = models.CharField("nba team's name", max_length=255, unique=True)
    description = models.TextField("nba team's description")
    conference = models.CharField("nba team's conference", max_length=255)
    division = models.CharField("nba team's division", max_length=255)
    stadium = models.CharField("nba team's home stadium", max_length=255)
    api_id = models.IntegerField("id for api identification", null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Player(models.Model):
    name = models.CharField("player's name", unique=True, max_length=255)
    team_id = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        verbose_name="player's team",
        null=True,
        blank=True,
    )

    api_id = models.IntegerField("id for api identification", null=True, blank=True)

    birth_date = models.DateField("player's birth date", null=True, blank=True)
    citizenship = models.CharField(
        "player's citizenship", max_length=255, null=True, blank=True
    )
    height_feet = models.CharField(
        "player's height, feet part", max_length=10, null=True, blank=True
    )
    height_inches = models.CharField(
        "player's height, inches part", max_length=10, null=True, blank=True
    )
    height_meters = models.CharField(
        "player's height in meters", max_length=10, null=True, blank=True
    )
    weight_pounds = models.CharField(
        "player's weight in pounds", max_length=10, null=True, blank=True
    )
    weight_kilograms = models.CharField(
        "player's weight in kilograms", max_length=10, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class Game(models.Model):
    home_team_id = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name="home team",
        related_name="home_team_id",
    )
    guest_team_id = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name="guest team",
        related_name="guest_team_id",
    )
    date_time = models.DateTimeField(verbose_name="Game's date time")
    api_id = models.IntegerField("id for api identification", null=True, blank=True)

    home_team_score = models.IntegerField("home team score")
    guest_team_score = models.IntegerField("guest team score")

    quarter1_home_score = models.IntegerField("quarter1 home score")
    quarter1_guest_score = models.IntegerField("querter1 guest score")
    quarter2_home_score = models.IntegerField("quarter2 home score")
    quarter2_guest_score = models.IntegerField("quarter2 guest score")
    quarter3_home_score = models.IntegerField("quarter3 home score")
    quarter3_guest_score = models.IntegerField("quarter3 guest score")
    quarter4_home_score = models.IntegerField("quarter4 home score")
    quarter4_guest_score = models.IntegerField("quarter4 guest score")

    home_team_attempts = models.IntegerField("home team attempts")
    home_team_field_goal_pct = models.FloatField("home team fg%")
    home_team_3p_pct = models.FloatField("home team 3p%")
    home_team_rebounds = models.IntegerField("home team rebounds")
    guest_team_attempts = models.IntegerField("guest team attempts")
    guest_team_field_goal_pct = models.FloatField("guest team fg%")
    guest_team_3p_pct = models.FloatField("guest team 3p%")
    guest_team_rebounds = models.IntegerField("guest team rebounds")

    mvp_id = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        verbose_name="MVP of the game",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return (
            f"{Team.objects.get(id=self.home_team_id).name} ({self.home_team_score}) - "
            + f"({self.guest_team_score}) {Team.objects.get(id=self.guest_team_id).name}"
        )

    class Meta:
        ordering = ["-date_time"]


class PlayerStatisticPerGame(models.Model):
    player_id = models.ForeignKey(
        Player, on_delete=models.CASCADE, verbose_name="player id"
    )
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="game id")
    api_id = models.IntegerField("id for api identification")
    scored_points = models.IntegerField("amount of scored points")
    minutes_on_field = models.CharField(
        max_length=10, verbose_name="players time on field"
    )
    position = models.CharField(max_length=10, verbose_name="player's position")
    fgm = models.IntegerField("field goal made")
    fga = models.IntegerField("field goal attempts")
    fgp = models.CharField(max_length=10, verbose_name="field goal percentage")
    ftm = models.IntegerField("field throw made")
    fta = models.IntegerField("field throw attempts")
    ftp = models.CharField(max_length=10, verbose_name="field throw percentage")
    tpm = models.IntegerField("three points made")
    tpa = models.IntegerField("three points attempts")
    tpp = models.CharField(max_length=10, verbose_name="three points percentage")
    offReb = models.IntegerField("offensive rebounds")
    defReb = models.IntegerField("defensive rebounds")
    totReb = models.IntegerField("total rebounds")
    assists = models.IntegerField("total assists")
    pFoulds = models.IntegerField("personal fouls")
    steals = models.IntegerField("steals")
    turnovers = models.IntegerField("turnovers")
    blocks = models.IntegerField("blocks")
