#ifndef USERWIDGET_H
#define USERWIDGET_H

#include <QWidget>

#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonObject>

#include <QVariantList>
#include <QVariantMap>

#include <QComboBox>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class UserWidget;
}

class UserWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit UserWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~UserWidget();

    void setData(const TeraData* data);

    void saveData(bool signal=true);

    bool dataIsNew();

    void deleteData();

    void setLimited(bool limited);

    void connectSignals();

    void processQueryReply(const QString &path, const QUrlQuery &query_args, const QString &data);
    void processPostReply(const QString &path, const QString &data);

private:
    Ui::UserWidget* ui;

    bool                m_limited; // Current user editing only
    QMap<int, int>      m_tableSites_ids_rows;
    QMap<int, int>      m_tableProjects_ids_rows;
    QString             m_userprojects;
    QString             m_usersites;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

    void fillSites(const QString& sites_json);
    void fillSitesData();
    void fillProjects(const QString& projects_json);
    void fillProjectsData();
    QComboBox *buildRolesComboBox();

public slots:


private slots:
    void btnEdit_clicked();
    void btnDelete_clicked();
    void btnSave_clicked();
    void txtPassword_textChanged(const QString &new_pass);
    void btnUndo_clicked();
};



#endif // USERWIDGET_H
