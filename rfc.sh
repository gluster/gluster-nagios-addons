#!/bin/bash

ME=$(basename $0)

editormode=0
askbugid=0
branch="master"
dryrun=0
fetch=1
topic=""


show_help()
{
    cat 1>&2 <<EOF
Usage: $ME [OPTION]... [ <REVIEWER> ]...

Options:
  -a               ask for Bug ID addition.  This option is set by default for
                   non 'master' branches.
  -b BRANCH        use BRANCH to submitting patch.  Default branch is 'master'.
  -d               dry run.  Show what command to run.
  -n               do not fetch origin.
  -t TOPIC         use TOPIC to submitting patch.
  -h               display this help text and exit.


By default, BUGID is used as topic in patch submission.  If TOPIC and
BUGID are used together, TOPIC gets used.

Examples:

# submit patch to master branch without reviewer
$ $ME

# submit patch to master branch with reviewer
$ $ME charlie@example.com

# submit patch to release-3.0 branch with topic "awesome feature" and
# reviewers charlie@example.com alice@example.com
$ $ME -b release-3.0 -t "awesome feature" charlie@example.com alice@example.com

EOF
}


is_num()
{
    test "$1" -eq "$1" 2>/dev/null
}


exit_editor_mode()
{
    if [[ "$1" =~ /git-rebase-todo$ ]]; then
        sed -i 's/^pick /reword /' "$1"
        exit 0
    fi

    if [[ "$1" =~ /COMMIT_EDITMSG$ ]]; then
        if grep -qi '^BUG:' "$1"; then
            exit 0
        fi

        if [ "$askbugid" -eq 0 ]; then
            #echo "warning: no Bug ID found" 1>&2
            exit 0
        fi

        while true; do
            echo "Commit: $(head -n 1 $1)"
            echo -n "Enter Bug ID: "
            read bug

            if [ -z "$bug" ]; then
                echo -e "ignored adding Bug ID\n" 1>&2
                exit 0
            fi

            if ! is_num "$bug"; then
                echo "invalid Bug ID '$bug'" 1>&2
                continue
            fi

            echo
            sed "/^Change-Id:/i BUG: $bug" "$1"
            exit 0
        done
    fi

    exit 1
}


add_hook_commit_msg()
{
    f=".git/hooks/commit-msg"
    u="http://review.gluster.org/tools/hooks/commit-msg"

    if [ -x "$f" ]; then
        return
    fi

    curl -k -o $f $u || wget --no-check-certificate -O $f $u

    chmod +x .git/hooks/commit-msg

    # Let the 'Change-Id: ' header get assigned on first run of rfc.sh
    GIT_EDITOR=true git commit --signoff --cleanup=whitespace --amend
}


assert_python_check()
{
    pyfiles=$(git diff --name-only origin/$branch..HEAD 2>/dev/null | grep -e '\.py$' -e '\.py\.in$')
    if [ -z "$pyfiles" ]; then
        return
    fi
    if ! pyflakes $pyfiles; then
        echo -e "\nPlease clear pyflakes error(s) before submission" 1>&2
        exit 1
    fi
    if ! pep8 -r --show-pep8 $pyfiles; then
        echo -e "\nPlease clear pep8 error(s) before submission" 1>&2
        exit 1
    fi
}


assert_rebase()
{
    if [ "$askbugid" -eq 1 -o "$branch" != "master" ]; then
        GIT_EDITOR="$0 -E -a" git -c 'commit.status=false' -c 'commit.cleanup=whitespace' rebase -i origin/$branch || exit 2
    else
        GIT_EDITOR="$0 -E" git -c 'commit.status=false' -c 'commit.cleanup=whitespace' rebase -i origin/$branch || exit 2
    fi
}


assert_nochange()
{
    if ! git diff origin/$branch..HEAD 2>/dev/null | grep -q .; then
        echo "No change to submit" 1>&2
        exit 3
    fi
}


main()
{
    # A POSIX variable
    OPTIND=1         # Reset in case getopts has been used previously in the shell.

    while getopts "Eab:dnt:h" opt; do
        case "$opt" in
            E)
                editormode=1
                ;;
            a)
                askbugid=1
                ;;
            b)
                branch=$OPTARG
                ;;
            d)
                dryrun=1
                ;;
            n)
                fetch=0
                ;;
            t)
                topic="$OPTARG"
                ;;
            h)
                show_help
                exit 0
                ;;
            \?)
                show_help
                exit -1
                ;;
        esac
    done

    shift $((OPTIND-1))

    [ "$1" = "--" ] && shift

    if [ $editormode -eq 1 ]; then
        exit_editor_mode "$@"
    fi

    for i; do
        if [[ ! "$i" =~ .*@.*\..*$ ]]; then
            echo "invalid email id: $i" 1>&2
            show_help
            exit -1
        fi
    done

    ref="HEAD:refs/for/${branch}%"

    if [ $dryrun -eq 1 ]; then
        drier='echo command: '
    else
        drier=
    fi

    if [ -n "$topic" ]; then
        topic=$(echo $topic | sed 's| |/|g')
        ref="${ref}topic=$topic,"
    elif [ -n "$bugid" ]; then
        ref="${ref}topic=bug-$bugid,"
    fi

    reviewers=( "$@" )
    reviewers=$(IFS=,; echo "${reviewers[*]/#/r=}")
    [ -n "$reviewers" ] && ref="$ref$reviewers"

    add_hook_commit_msg
    assert_python_check
    [ $fetch -eq 1 ] && git fetch origin
    assert_rebase
    assert_nochange

    $drier git push origin $ref

    if [ -z "$reviewers" ]; then
        echo -e "\nPatch is submitted without any reviewer.  Please add manually"
    fi
}

main "$@"
