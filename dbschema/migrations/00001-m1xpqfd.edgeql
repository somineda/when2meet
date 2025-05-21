CREATE MIGRATION m1xpqfd55qva3h6lyfap7cznascb2h45udfn5onblv2tldi53fndaa
    ONTO initial
{
  CREATE ABSTRACT TYPE default::Auditable {
      CREATE REQUIRED PROPERTY created_at: cal::local_datetime {
          SET default := (cal::to_local_datetime(std::datetime_current(), 'Asia/Seoul'));
          SET readonly := true;
      };
  };
  CREATE TYPE default::Meeting EXTENDING default::Auditable {
      CREATE REQUIRED PROPERTY url_code: std::str {
          SET readonly := true;
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
