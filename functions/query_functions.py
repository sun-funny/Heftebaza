from sqlalchemy import func
# Округа и регионы
def fo_region_query(base_query, tab_region_d314, tab_fo_d314):
    return (base_query.with_entities(
        tab_region_d314.name.label('region')
    ).join(
    tab_fo_d314, tab_fo_d314.id == tab_region_d314.tab_fo_d314_ids
    ).group_by(
        tab_region_d314.name,
    ).order_by(
        tab_region_d314.name
    )
    )
def region_fo_query(base_query, tab_region_d314, tab_fo_d314):
    return (base_query.with_entities(
        tab_fo_d314.name.label('fo')
    ).join(
    tab_region_d314, tab_fo_d314.id == tab_region_d314.tab_fo_d314_ids
    ).group_by(
        tab_fo_d314.name,
    ).order_by(
        tab_fo_d314.name
    )
    )
# Запросы для мэппингов
def mapping_query(base_query, tab):
    return (base_query.with_entities(
        tab.name.label('name'),
        tab.id.label('id')
    ).group_by(
        tab.name,
        tab.id
    ).order_by(
        tab.name
    ).filter(tab.id.not_in([19])
    )
    )

def year_query(base_query, tab_dataset_real_gaz_d314):
    return (base_query.with_entities(
        tab_dataset_real_gaz_d314.year.label('year')
    ).group_by(
        tab_dataset_real_gaz_d314.year
    ).order_by(
        tab_dataset_real_gaz_d314.year
    )
    )

def month_query(base_query, tab_dataset_real_gaz_d314):
    return (base_query.with_entities(
        tab_dataset_real_gaz_d314.month.label('month')
    ).group_by(
        tab_dataset_real_gaz_d314.month
    ).order_by(
        tab_dataset_real_gaz_d314.month
    )
    )