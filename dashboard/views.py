from typing import List, Union, Dict, Tuple
from django.shortcuts import render
from dashboard.models import Voting, IndividualVoting, Politician
import datetime
from django.db.models import Count, query
from urllib.parse import unquote
from django.views.decorators.http import require_http_methods
from dashboard.forms import DateForm


# TODO: keep order of vote_options, however get the list dynamically
# TODO: date_form und vote_options aus den views auslagern
@require_http_methods(["GET", "POST"])
def index(request):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    latest_votings: query.QuerySet = Voting.objects.filter(date__range=(start_date, end_date))
    votings_count: int = latest_votings.count()
    voting_ids: List[int] = [voting.voting_id for voting in latest_votings]

    factions: query.QuerySet = IndividualVoting.objects.filter(voting_id__in=voting_ids).\
        values_list('politician__faction', flat=True).distinct()

    faction_votes: Dict[str, Dict[str, int]] = {key: {vote: 0 for vote in vote_options} for key in factions}

    politician_votes: query.QuerySet = IndividualVoting.objects.filter(voting_id__in=voting_ids).\
        values_list('politician__faction', 'vote')

    total_votes: Dict[str, int] = {i: IndividualVoting.objects.filter(voting_id__in=voting_ids, vote=i).
        count() for i in vote_options}

    for i in politician_votes:
        faction_votes[i[0]][i[1]] += 1

    latest_genres: query.QuerySet = latest_votings.values_list('genre', flat=True)

    # TODO: perform aggregation operation in query
    genres: Dict[str, int] = {}
    for genre in latest_genres:
        if genres.get(genre) is not None:
            genres[genre] += 1
        else:
            genres[genre] = 0

    # TODO: perform filtering operation in query
    # remove genres that did not appear in the designated time span
    genres = {k: v for k, v in genres.items() if v > 0}

    # needed for charts
    genre_counts: List[int] = [value for value in genres.values()]
    genre_labels: List[str] = [key for key in genres.keys()]

    last_ten_votings: query.QuerySet = Voting.objects.all().order_by('-date')[:10]

    return render(request, 'dashboard/index.html', {'votings_count': votings_count,
                                                    'genre_labels': genre_labels,
                                                    'genre_counts': genre_counts,
                                                    'faction_votes': faction_votes,
                                                    'total_votes': total_votes,
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'date_form': date_form,
                                                    'last_ten_votings': last_ten_votings})


def list(request):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    all_votings: query.QuerySet = Voting.objects.filter(date__range=(start_date, end_date)).order_by('-date')

    return render(request, 'dashboard/list.html', locals())


def detail(request, voting_id):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    specific_voting: Voting = Voting.objects.filter(voting_id=voting_id)[0]
    # get politicians related to this specific voting
    pol_objects: query.QuerySet = Voting.objects.get(voting_id=voting_id).politicians.all().\
        order_by('individualvoting__politician_id')

    # get respective politician's vote - order as previous query!
    pol_votes: query.QuerySet = IndividualVoting.objects.filter(voting_id=voting_id).order_by('politician_id').\
        values_list('vote', flat=True)

    politicians: Tuple[query.QuerySet, query.QuerySet] = tuple(zip(pol_objects, pol_votes))
    factions: query.QuerySet = IndividualVoting.objects.filter(voting_id=voting_id).\
        values_list('politician__faction', flat=True).distinct()

    # needed for charts, remove the key "Summe"
    vote_labels: List[str] = [key for key in specific_voting.votes.keys() if key != 'Summe']
    votes: List[int] = [int(v) for k, v in specific_voting.votes.items() if k != 'Summe']

    cells: query.QuerySet = IndividualVoting.objects.filter(voting_id=voting_id).values('politician__faction',
                                                                                        'vote').annotate(Count('vote'))
    objects: Dict[str, Dict[str, int]] = {}
    for cell in cells:
        objects.setdefault(cell['politician__faction'], {})[cell['vote']] = cell['vote__count']

    labels: List[str] = [key for key in objects.keys()]

    vote_counts: List[List[int]] = [[0 for _ in labels] for _ in vote_options]
    for idx, faction in enumerate(labels):
        for vote in vote_options:
            if objects.get(faction).get(vote):
                vote_counts[vote_options.index(vote)][idx] = objects[faction][vote]

    return render(request, 'dashboard/detail.html', locals())


@require_http_methods(["GET", "POST"])
def genre_votes(request, name):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    votings: query.QuerySet = Voting.objects.filter(date__range=(start_date, end_date), genre=name)

    cells: query.QuerySet = IndividualVoting.objects.filter(voting__date__range=(start_date, end_date),
                                                            voting__genre=name).values('politician__faction',
                                                                                       'vote').annotate(Count('vote'))

    objects: Dict[str, Dict[str, int]] = {}
    for cell in cells:
        objects.setdefault(cell['politician__faction'], {})[cell['vote']] = cell['vote__count']

    labels: List[str] = [key for key in objects.keys()]

    vote_counts: List[List[int]] = [[0 for _ in labels] for _ in vote_options]
    for idx, faction in enumerate(labels):
        for vote in vote_options:
            if objects.get(faction).get(vote):
                vote_counts[vote_options.index(vote)][idx] = objects[faction][vote]

    return render(request, 'dashboard/genre_votes.html', locals())


@require_http_methods(["GET", "POST"])
def faction_votes(request, name):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    name: str = unquote(name)
    votings: query.QuerySet = Voting.objects.filter(date__range=(start_date, end_date), politicians__faction=name).distinct()

    cells: query.QuerySet = IndividualVoting.objects.filter(voting__date__range=(start_date, end_date),
                                            politician__faction=name).values('voting__genre',
                                                                             'vote').annotate(Count('vote'))
    objects: Dict[str, Dict[str, int]] = {}

    for cell in cells:
        objects.setdefault(cell['voting__genre'], {})[cell['vote']] = cell['vote__count']

    genre_labels: List[str] = [k for k in objects.keys()]
    genre_votes_count: List[List[int]] = [[0 for _ in genre_labels] for _ in vote_options]

    for idx, genre in enumerate(genre_labels):
        for vote in vote_options:
            if objects.get(genre).get(vote):
                genre_votes_count[vote_options.index(vote)][idx] = objects[genre][vote]

    return render(request, 'dashboard/faction_votes.html', locals())


@require_http_methods(['GET', 'POST'])
def politician(request, politician_id):
    vote_options: List[str] = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    date_form: DateForm = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date: str = date_form.fields['start_date'].initial
    start_date: datetime.date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date: str = date_form.fields['end_date'].initial
    end_date: datetime.date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
        else:
            # Todo: frontend notification for invalid data
            print("data invalid")

    politician_query: query.QuerySet = Politician.objects.filter(id=politician_id)
    politician: Union[Politician, None] = politician_query[0] if len(politician_query) != 0 else None

    if politician is None:
        response = f"Ein Politiker mit der ID {politician_id} konnte nicht gefunden werden."
        return render(request, 'dashboard/error.html', {'error': response})

    last_voting: query.QuerySet = Voting.objects.filter(politicians__id=politician_id).order_by('-date').values('date')

    if len(last_voting) > 0:
        last_voting = last_voting[0]

    votings: query.QuerySet = Voting.objects.filter(politicians__id=politician_id, date__range=(start_date, end_date)).order_by('-date')

    individual_votes: query.QuerySet = IndividualVoting.objects.\
        filter(politician__id=politician_id, voting_id__in=votings.
               values_list('voting_id', flat=True)).values_list('vote', flat=True)

    voting_count: int = votings.count()
    vote_stats_genre: query.QuerySet = IndividualVoting.objects.\
        filter(politician__id=politician_id, voting__date__range=(start_date, end_date)).\
        values('voting__genre', 'vote').annotate(Count('vote'))

    vote_stats_query: query.QuerySet = IndividualVoting.objects.\
        filter(politician__id=politician_id, voting__date__range=(start_date, end_date)).\
        values_list('vote').annotate(Count('vote'))

    # TODO: reihenfolge und existenz der voteoptionen sicherstellen
    opt_stats: List[int] = []
    for vote_opt in vote_options:
        found = False
        for tuple_ in vote_stats_query:
            if tuple_[0] == vote_opt:
                opt_stats.append(tuple_[1])
                found = True
        if not found:
            opt_stats.append(0)

    vote_stats: List[List[str], List[int]] = [vote_options, opt_stats]
    objects: Dict[str, Dict[str, int]] = {}

    for cell in vote_stats_genre:
        objects.setdefault(cell['voting__genre'], {})[cell['vote']] = cell['vote__count']

    # needed for charts
    genre_counts_yes: List[int] = [options.get('Ja') if options.get('Ja') else 0 for options in objects.values()]
    genre_counts_no: List[int] = [options.get('Nein') if options.get('Nein') else 0 for options in objects.values()]
    genre_counts_not_turned_in: List[int] = [options.get('Nicht abgegeben') if options.get('Nicht abgegeben') else 0 for options in objects.values()]
    genre_counts_enthalten: List[int] = [options.get('Enthalten') if options.get('Enthalten') else 0 for options in objects.values()]
    genre_options_count: List[int] = [genre_counts_yes, genre_counts_no, genre_counts_not_turned_in, genre_counts_enthalten]

    genre_counts: List[int] = [value for value in objects.values()]
    genre_labels: List[str] = [key for key in objects.keys()]

    return render(request, 'dashboard/politician.html', locals())
