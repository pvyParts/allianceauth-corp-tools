import os

from bravado.exception import HTTPError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Count, F, Sum, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from esi.decorators import token_required
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from django.http import HttpResponse
import csv
import re
import copy

from ..models import *

def get_alts(request, character_id):
    if character_id is None:
        main_char = request.user.profile.main_character
    else:
        main_char = EveCharacter.objects.get_character_by_id(character_id).character_ownership.user.profile.main_character

    character_id = main_char.character_id
    characters = CharacterAudit.objects.get(character__character_id=character_id).character.character_ownership.user.character_ownerships.all().select_related('character', 'character__characteraudit')
    net_worth = 0
    for character in characters:
        try:
            net_worth+=character.character.characteraudit.balance
        except:
            pass
    return main_char, characters, net_worth

@login_required
def assets(request, character_id=None):
    # get available models

    main_char, characters, net_worth = get_alts (request, character_id)

    capital_groups = [30, 547, 659, 1538, 485, 902, 513, 944, 941]
    subcap_cat = [6]
    noteable_cats = [4, 20, 23, 25, 34, 35, 87, 91]
    structure_cats = [22, 24, 40, 41, 46, 65, 66,]
    bpo_cats = [9]

    assets = CharacterAsset.objects\
                .filter(character__character__character_id__in=characters.values_list('character__character_id', flat=True))\
                .values('type_name__group__group_id')\
                .annotate(grp_total=Sum('quantity'))\
                .annotate(grp_name=F('type_name__group__name'))\
                .annotate(grp_id=F('type_name__group_id'))\
                .annotate(cat_id=F('type_name__group__category_id'))\
                .order_by('-grp_total')
    
    capital_asset_groups = []
    subcap_asset_groups = []
    noteable_asset_groups = []
    structure_asset_groups = []
    bpo_asset_groups = []
    remaining_asset_groups = []

    for grp in assets:
        if grp['grp_id'] in capital_groups:
            capital_asset_groups.append(grp)
        elif grp['cat_id'] in subcap_cat:
            subcap_asset_groups.append(grp)
        elif grp['cat_id'] in noteable_cats:
            noteable_asset_groups.append(grp)
        elif grp['cat_id'] in structure_cats:
            structure_asset_groups.append(grp)
        elif grp['cat_id'] in bpo_cats:
            bpo_asset_groups.append(grp)
        else:
            remaining_asset_groups.append(grp)
        
    context = {
        "main_char": main_char,
        "alts": characters,
        "net_worth": net_worth,
        "capital_asset_groups": capital_asset_groups,
        "noteable_asset_groups": noteable_asset_groups,
        "subcap_asset_groups": subcap_asset_groups,
        "structure_asset_groups": structure_asset_groups,
        "bpo_asset_groups": bpo_asset_groups,
        "remaining_asset_groups": remaining_asset_groups
    }

    return render(request, 'corptools/character/assets.html', context=context)

@login_required
def wallet(request, character_id=None):
    # get available models

    main_char, characters, net_worth = get_alts (request, character_id)

    wallet_journal = CharacterWalletJournalEntry.objects\
                        .filter(character__character__character_id__in=characters.values_list('character__character_id', flat=True))\
                        .select_related('first_party_name', 'second_party_name', 'character__character')
    
    graph_data_model = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0}
    # %-H	
    graph_data = {}
    for wd in wallet_journal:
        if wd.character.character.character_name not in graph_data:
            graph_data[wd.character.character.character_name] = copy.deepcopy(graph_data_model)
        graph_data[wd.character.character.character_name][wd.date.strftime("%-H")] += 1

    context = {
        "main_char": main_char,
        "alts": characters,
        "net_worth": net_worth,
        "wallet": wallet_journal,
        "graphs": graph_data,
    }

    return render(request, 'corptools/character/wallet.html', context=context)

@login_required
def pub_data(request, character_id=None):
    # get available models

    main_char, characters, net_worth = get_alts (request, character_id)
    character_ids = characters.values_list('character__character_id', flat=True)
    corp_histories = CorporationHistory.objects\
                        .filter(character__character__character_id__in=character_ids)\
                        .select_related('character__character', 'corporation_name')
    char_skill_total = Skill.objects\
                        .filter(character__character__character_id__in=character_ids)\
                        .values('character')\
                        .annotate(char=F('character__character__character_name'))\
                        .annotate(total_sp=Sum('skillpoints_in_skill'))

    bios = None

    table_data = {}
    for char in characters:
        table_data[char.character.character_name] = {"character":char.character,"history":{},"bio":"Nothing of value is here"}

    for h in corp_histories:
        table_data[h.character.character.character_name]["history"][str(h.record_id)] = {"name": h.corporation_name.name, "id":h.corporation_id, "started":h.start_date, "open": h.is_deleted}

    for c in char_skill_total:
        table_data[c.get('char')]["total_sp"] = c.get('total_sp')

    context = {
        "main_char": main_char,
        "alts": characters,
        "net_worth": net_worth,
        "table_data": table_data,
    }

    return render(request, 'corptools/character/public.html', context=context)
